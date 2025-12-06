from __future__ import annotations
from dataclasses import dataclass, field
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
        prices = price_map[self.Ticker.name]
        # TODO: Why not updating the ticker prices here?
        if prices:
            if self.YesOrNo == "YES":
                self.CurrentPrice = prices[0]
            else:
                self.CurrentPrice = prices[1]

    def unrealized_pnl(self):
        return (self.CurrentPrice - self.PurchasePrice) * self.NumberOfContracts if not self.isActive else 0.0


@dataclass
class Ledger:
    Trades: List[Trade]
    LiquidValue: float = 1000.0      # starting value of the ledger
    Profit: float = 0.0
    # Need some way to track historical performance I feel

    def add_trade(self, trade: Trade) -> None:
        self.trades.append(trade)

    # State Manager
    def updateLedger(self, price_map: Dict[str, Tuple[float, float]], injected_capital: float):
        """
        1. Go through all trades in ledger
        2. Update profit value
        3. Update liquid value if required
        :return:
        """
        # update trades in ledger and update PNL
        pnl = 0.0

        for trade in self.Trades:
            trade.update_trade(price_map)
            pnl += trade.unrealized_pnl()

        if injected_capital:
            self.LiquidValue += injected_capital

        self.Profit = pnl

        print("\nLedger updated\nCash Balance: {self.LiquidValue}\nPNL: {self.Profit}\n\n")





