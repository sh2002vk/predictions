from components import Ledger, MarketState, TradeSignal
from strategies.strategy import Strategy

class Rando(Strategy):
    def compute(self, market_state: MarketState, ledger: Ledger):
        if market_state.yes_price + market_state.no_price < 1.0:
            return TradeSignal(
                action="BUY",
                side="YES",
                quantity=10,
                price=market_state.yes_price
            )
        return None