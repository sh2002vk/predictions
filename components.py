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
    LastUpdated: float = 0.0    # epoch of last update

    def updateTicker(self, yesPrice: float, noPrice: float, time: float):
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
    Ticker: Ticker              # ticker being traded
    PurchasePrice: float        # purchase price of contract
    PurchaseTime: float         # epoch of purchase
    SaleTime: Optional[float]   # epoch of sale
    ContractType: str           # TODO: WHAT HAPPENS TO THIS ONE
    YesOrNo: str                # TODO: make into enum of Yes or No
    NumberOfContracts: int      # num of contracts purchased
    CurrentPrice: float = 0.0   # current price PER contract
    isActive: bool = False      # bool of whether trade is live or not

    def update_trade(self, price_map: Dict[str, Tuple[float, float]]):
        """ PriceMap: {Ticker: [yesPrice, noPrice]} """
        prices = price_map.get(self.Tickername)
        if prices:
            if self.YesOrNo == "YES":
                self.CurrentPrice = prices[0]
            else:
                self.CurrentPrice = prices[1]

        self.Ticker.updateTicker(prices[0], prices[1], time=self.PurchaseTime)

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


@dataclass
class Ledger:
    Trades: List[Trade] = None
    LiquidValue: float = 1000.0      # starting value of the ledger
    Profit: float = 0.0
    # Need some way to track historical performance I feel

    def addTrade(self, trade: Trade) -> None:
        self.Trades.append(trade)

    def buildPriceMap(self):
        # {str: [yesPrice, noPrice]}
        if not self.Trades:
            return
        resp = {}
        for trade in self.Trades:
            if trade["app"]:
                resp[trade["app"]] = [trade["yesOutcome"], trade["noOutcome"]]
        return resp

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








