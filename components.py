from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class Ticker:
    Name: str
    YesPrice: float = 0.0
    NoPrice: float = 0.0
    RealRank: int = 0           # rank from app store
    PotentialRank: int = 0      # implied rank on polymarket
    LastUpdated: int = 0    # epoch of last update

    def updateTicker(self, yesPrice: float, noPrice: float, time: int):
        self.YesPrice = yesPrice
        self.NoPrice = noPrice
        self.LastUpdated = time

    def __str__(self) -> str:
        return (
            f"Ticker: {self.Name}\n"
            f"  Yes: {self.YesPrice:.3f} | No: {self.NoPrice:.3f}\n"
            f"  Real Rank: {self.RealRank} | Potential Rank: {self.PotentialRank}\n"
            f"  Last Updated (epoch): {self.LastUpdated}"
        )


@dataclass
class Trade:
    Ticker: Ticker                # ticker being traded
    PurchasePrice: float          # purchase price of contract
    PurchaseTime: Optional[float] # epoch of purchase
    SaleTime: Optional[float]     # epoch of sale
    YesOrNo: str                  # TODO: make into enum of Yes or No
    NumberOfContracts: int        # num of contracts purchased
    CurrentPrice: float = 0.0     # current price PER contract
    isActive: bool = False        # bool of whether trade is live or not

    def update_trade(self, price_map: Dict[str, Tuple[float, float]], timestamp: Optional[int] = None):
        """ 
        PriceMap: {Ticker: [yesPrice, noPrice]}
        timestamp: Current time for updating LastUpdated. If None, uses PurchaseTime.
        """
        prices = price_map.get(self.Ticker.Name)
        if prices:
            if self.YesOrNo == "YES":
                self.CurrentPrice = prices[0]
            else:
                self.CurrentPrice = prices[1]
            
            # Use provided timestamp, or fall back to PurchaseTime if not provided
            update_time = timestamp if timestamp is not None else self.PurchaseTime
            self.Ticker.updateTicker(prices[0], prices[1], time=update_time)

    def unrealized_pnl(self):
        return (self.CurrentPrice - self.PurchasePrice) * self.NumberOfContracts if self.isActive else 0.0

    def __str__(self) -> str:
        status = "ACTIVE" if self.isActive else "CLOSED"
        side = self.YesOrNo.upper()
        pnl = self.unrealized_pnl()

        return (
            f"Trade on {self.Ticker.Name} [{status}] ({side})\n"
            f"  Qty: {self.NumberOfContracts}\n"
            f"  Entry: {self.PurchasePrice:.3f} | Current: {self.CurrentPrice:.3f}\n"
            f"  Purchase Time (epoch): {self.PurchaseTime}\n"
            f"  Sale Time (epoch): {self.SaleTime}\n"
            f"  Unrealized PnL: {pnl:.2f}"
        )

    def to_row(self) -> str:
        """Single-line row for ledger view."""
        status = "ACTIVE" if self.isActive else "CLOSED"
        side = self.YesOrNo.upper()
        pnl = self.unrealized_pnl()

        return (
            f"{self.Ticker.Name:<20}"
            f"{self.YesOrNo:^6}"
            f"{self.NumberOfContracts:>6}"
            f"{self.PurchasePrice:>12.3f}"
            f"{self.CurrentPrice:>13.3f}"
            f"{pnl:>14.2f}"
            f"{status:>8}"
        )


class Ledger:
    def __init__(self):
        self.Trades: List[Trade] = []
        self.LiquidValue: float = 1000.0      # starting value of the ledger
        self.Profit: float = 0.0
        # Need some way to track historical performance I feel

    def addTrade(self, trade: Trade) -> None:
        self.Trades.append(trade)

    def buildPriceMap(self):
        # {str: [yesPrice, noPrice]}
        if not self.Trades:
            return {}
        resp = {}
        for trade in self.Trades:
            if trade.isActive and trade.Ticker:
                ticker_name = trade.Ticker.Name
                # get prices from the ticker's current state
                resp[ticker_name] = (trade.Ticker.YesPrice, trade.Ticker.NoPrice)
        return resp
    
    def executeTrade(self, signal: TradeSignal, ticker_name: str, timestamp: int):
        # handle SELL operations
        if signal.action == "SELL":
            # find matching active trades (same ticker, same side)
            matching_trades = [
                trade for trade in self.Trades
                if trade.isActive 
                and trade.Ticker.Name == ticker_name 
                and trade.YesOrNo == signal.side
            ]
            
            if not matching_trades:
                print(f"No active trades to sell for {ticker_name} ({signal.side}) at {timestamp}")
                return False
            
            # total available contracts to sell
            total_available = sum(trade.NumberOfContracts for trade in matching_trades)
            
            if signal.quantity > total_available:
                print(f"Not enough contracts to sell. Requested: {signal.quantity}, Available: {total_available} for {ticker_name} at {timestamp}")
                return False
            
            # execute sell: close trades starting from oldest first
            remaining_to_sell = signal.quantity
            sale_proceeds = 0.0
            
            for trade in matching_trades:
                if remaining_to_sell <= 0:
                    break
                
                if trade.NumberOfContracts <= remaining_to_sell:
                    # close entire trade because number of contracts to sell is greather than those in the trade
                    contracts_to_sell = trade.NumberOfContracts
                    trade.CurrentPrice = signal.price  
                    trade.isActive = False
                    trade.SaleTime = timestamp
                    sale_proceeds += contracts_to_sell * signal.price
                    remaining_to_sell -= contracts_to_sell
                else:
                    # partial sell - split the trade because less remaining to sell than in this contract
                    contracts_to_sell = remaining_to_sell
                    closed_trade = Trade(
                        Ticker=trade.Ticker,
                        PurchasePrice=trade.PurchasePrice,
                        PurchaseTime=trade.PurchaseTime,
                        SaleTime=timestamp,
                        YesOrNo=trade.YesOrNo,
                        NumberOfContracts=contracts_to_sell,
                        CurrentPrice=signal.price,  
                        isActive=False
                    )
                    self.Trades.append(closed_trade)
                    # eeduce the active trade's quantity
                    trade.NumberOfContracts -= contracts_to_sell
                    sale_proceeds += contracts_to_sell * signal.price
                    remaining_to_sell = 0
            
            # add sale proceeds back to liquid value
            self.LiquidValue += sale_proceeds
            return True
        
        # handle BUY operations 
        cost = signal.quantity * signal.price
        if cost > self.LiquidValue:
            print(f"Not enough liquid value to execute trade for {ticker_name} at {timestamp}")
            return False

        ticker = Ticker(Name=ticker_name)
        initial_price = signal.price  # Use purchase price as initial current price
        
        trade = Trade(
            Ticker=ticker,
            PurchasePrice=signal.price,
            PurchaseTime=timestamp,
            SaleTime=None,
            YesOrNo=signal.side,
            NumberOfContracts=signal.quantity,
            CurrentPrice=initial_price,  # Set initial price so PnL calculation works immediately
            isActive=True
        )
        self.LiquidValue -= cost
        self.Trades.append(trade)
        return True
    
    def update_ledger_at_time(self, timestamp: int, yes_price: float, no_price: float, ticker_name: str):
        # used for updates while backtesting
        pnl = 0.0
        price_map = {ticker_name: (yes_price, no_price)}
        
        for trade in self.Trades:
            if trade.isActive:
                trade.update_trade(price_map, timestamp=int(timestamp))
                pnl += trade.unrealized_pnl()
        
        self.Profit = pnl

    # State Manager
    def updateLedger(self, injected_capital: float):
        """
        1. Go through all trades in ledger
        2. Update profit value
        3. Update liquid value if required
        :return:
        """
        print(f"Updating Ledger.... \n\nState before update:")
        self.viewLedger()

        if not self.Trades:
            print("\nNo trades to update in ledger")
            return

        # update trades in ledger and update PNL
        pnl = 0.0
        price_map = self.buildPriceMap()

        for trade in self.Trades:
            trade.update_trade(price_map)
            pnl += trade.unrealized_pnl()

        if injected_capital:
            self.LiquidValue += injected_capital

        self.Profit = pnl

        print(f"Injected Capital: {injected_capital}\n"
              f"After Update: \n")
        self.viewLedger()

    def viewLedger(self):
        print("=== Ledger State ===")
        print(f"Cash Balance: {self.LiquidValue:.2f}")
        print(f"Unrealized PnL: {self.Profit:.2f}\n")

        print("Trades:\n")

        header = (
            f"{'Ticker':<20} "
            f"{'Side':^6} "
            f"{'Qty':>6} "
            f"{'Entry Price':>12} "
            f"{'Current Price':>13} "
            f"{'Unrealized PnL':>14} "
            f"{'Status':>8}"
        )

        print(header)
        print("-" * len(header))

        if not self.Trades:
            print("No trades in ledger")
            return

        for trade in self.Trades:
            print(trade.to_row())


@dataclass
class MarketState:
    timestamp: int
    yes_price: float
    no_price: float
    yes_token: str
    no_token: str
    ticker: str
    token: str

@dataclass
class TradeSignal:
    action: str  # "BUY", "SELL", or None/empty for no action
    side: str    # "YES" or "NO"
    quantity: int
    price: float

@dataclass
class Strategy:
    Title: str = None



