from abc import ABC, abstractmethod
from typing import Optional

from components import Ledger, MarketState, TradeSignal

class Strategy(ABC):
    
    @abstractmethod
    def compute(self, marketState: MarketState, ledger: Ledger) -> Optional[TradeSignal]:
        """
        Emits a TradeSignal if it is favorable based on the MarketState and Ledger
        """
        pass