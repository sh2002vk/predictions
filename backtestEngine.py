import pandas as pd

from components import Ledger, TradeSignal, MarketState
from polymarket_connector import *
from typing import Callable, List, Dict, Any, Optional
from dataclasses import dataclass
from grapher import *

# Format for Strategy : Marketstate, Ledger -> TradeSignal (but note this only looks at a given state, not behind)

@dataclass
class BacktestSnapshot:
    timestamp: int
    liquid_value: float
    unrealized_pnl: float
    total_value: float
    num_active_trades: int

class BacktestEngine:
    """Note that for markets that have CLOSED, build the price panel with start and end timestamps, it will not return useful data without it, the yes and no will be either 0or1
       
       Notes:
        - price_panel has format: t,token,no,yes,ticker,yes_token,no_token where t is timestamp
        - the index of the df is timestamp and token
        - it is not guaranteed that all tokens exist at all timestamps
        - it is not guaranteed that timestamps have a fixed interval
        - it will forward fill NaN price values with the last seen price
        - the engine should iterate through each record and generate signals based on the records, and ones seen before it
        - currently this is specified towards the app-store slug

       Potential causes for price_panel being empty:
        - the market has closed,  and start + end ts were not supplied
        - the market is too new and not traded enough to have outcomePrices and yesClob/noClob tokens in the API response from polymarket (TODO: LOOK INTO THIS)
    """

    def __init__(self, initial_capital: float):
        self.ledger = Ledger()
        self.ledger.LiquidValue = initial_capital
        self.snapshots: List[BacktestSnapshot] = []
    
    def build_price_panel(self, date: str, ffill: bool, free: bool, interval: Optional[str] = None, start_ts: Optional[int] = None, end_ts: Optional[int] = None):
        # THIS IS CUSTOM TO THE APP STORE RANKING, MODULARIZE THIS LATER
        # feed it the date and interval (1m, 1w, 1d, 6h, 1h, max)
        # ffill is option to use pandas to add in last seen price for NaN prices
        print('building price panel')
        polymarket = PolymarketConnector()
        order_book = OrderBook()
        apps = polymarket.get_app_store_rankings(free=free, date=date)

        prices: List[Dict[str, Any]] = []

        for app in apps:
            yes_clob_token, no_clob_token, ticker = app["yesClobToken"], app["noClobToken"], app["app"]
            # skip if ticker is missing or invalid
            if not ticker or not yes_clob_token or not no_clob_token:
                print('skipping')
                continue
            
            yes_param = { "market": yes_clob_token}
            no_param = { "market": no_clob_token}
            if start_ts is not None:
                yes_param["startTs"] = start_ts
                no_param["startTs"] = start_ts
            if end_ts is not None:
                yes_param["endTs"] = end_ts
                no_param["endTs"] = end_ts
            if interval is not None:
                yes_param["interval"] = interval
                no_param["interval"] = interval

            yes_prices = order_book.get_historical_prices(yes_param).get("history", [])  # to prevent empty response crash
            no_prices = order_book.get_historical_prices(no_param).get("history", [])  # to prevent empty response crash
            # using the yes token as the key to prevent name collisions. in the same daterange, the token should be the same

            for record in yes_prices:
                time, price = int(record["t"]), float(record["p"])
                prices.append({
                    "t": time,
                    "price": price,
                    "side": "yes",
                    "ticker": ticker,
                    "token": yes_clob_token,
                    "yes_token": yes_clob_token,
                    "no_token": no_clob_token
                })
            for record in no_prices:
                time, price = int(record["t"]), float(record["p"])
                prices.append({
                    "t": time,
                    "price": price,
                    "side": "no",
                    "ticker": ticker,
                    "token": yes_clob_token,
                    "yes_token": yes_clob_token,
                    "no_token": no_clob_token
                })

        if not prices:
            empty = pd.DataFrame(columns=["yes","no","ticker","yes_token","no_token"])
            empty.index = pd.MultiIndex.from_arrays([[], []], names=["t","token"])
            return empty
        
        df = pd.DataFrame(prices)

        # add yes, no into same row
        price_wide = (
            df.pivot_table(index=["t", "token"], columns="side", values="price", aggfunc="last")
            .sort_index()
        )

        # create metadata (ticker/tokens) per market table
        meta = (
            df.sort_values("t")
            .drop_duplicates(subset=["token"], keep="last")[["token", "ticker", "yes_token", "no_token"]]
            .set_index("token")
        )

        # price and meta table
        out = price_wide.reset_index().join(meta, on="token").set_index(["t", "token"]).sort_index()

        if ffill:
            out = (
                out.groupby(level="token", group_keys=False)
                .apply(lambda g: g.ffill())
            )
        
        return out

    def run(self, start_ts: int, end_ts: int, interval: str, strategy: Callable, date: str, ffill: bool, free: bool): 
        """
        TODO: - need to be able to execute MULTIPLE trade signals, instead of just one, per call to strategy function
        """
        
        print("starting backtest engine")
        prices = self.build_price_panel(date=date, interval=interval, ffill=ffill, start_ts=start_ts, end_ts=end_ts, free=free)       

        if prices.empty:
            print("price panel was empty")
            return {"ledger": self.ledger, "snapshots": self.snapshots}

        for t, frame in prices.groupby(level=0):
            # collect all prices for this timestamp
            price_map = {}
            
            # first pass: collect prices and execute trades
            for token, row in frame.droplevel(0).iterrows():
                yes_price = row.get("yes")
                no_price  = row.get("no")
                ticker    = row.get("ticker")
                yes_token = row.get("yes_token")
                no_token  = row.get("no_token")
            
                # skip if prices are missing or ticker is invalid
                if pd.isna(yes_price) or pd.isna(no_price) or not ticker:
                    continue
                
                # store prices for this ticker
                price_map[ticker] = (float(yes_price), float(no_price))
                
                market_state = MarketState(
                    timestamp=t,
                    ticker=ticker,
                    token=token,
                    yes_price=float(yes_price),
                    no_price=float(no_price),
                    yes_token=yes_token,
                    no_token=no_token,
                )

                trade_signal = strategy(market_state, self.ledger)  
                if trade_signal:
                    self.ledger.executeTrade(trade_signal, ticker, t)

            # second pass: update ledger with all prices for this timestamp
            if price_map:
                # update all active trades with current prices
                pnl = 0.0
                for trade in self.ledger.Trades:
                    if trade.isActive:
                        trade.update_trade(price_map, timestamp=t)
                        pnl += trade.unrealized_pnl()
                self.ledger.Profit = pnl

            # create snapshot once per timestamp (after processing all tokens)
            position_value = 0.0
            unrealized_pnl = 0.0

            for tr in self.ledger.Trades:
                if tr.isActive:
                    position_value += tr.CurrentPrice * tr.NumberOfContracts
                    unrealized_pnl += (tr.CurrentPrice - tr.PurchasePrice) * tr.NumberOfContracts

            snapshot = BacktestSnapshot(
                timestamp=t,
                liquid_value=self.ledger.LiquidValue,
                unrealized_pnl=unrealized_pnl,
                total_value=self.ledger.LiquidValue + position_value,
                num_active_trades=sum(1 for tr in self.ledger.Trades if tr.isActive),
            )
            self.snapshots.append(snapshot)
            
        return {
            "ledger": self.ledger,
            "snapshots": self.snapshots
        }


def strategyRando(market_state: MarketState, ledger: Ledger):
    if market_state.yes_price + market_state.no_price < 1.0:
        return TradeSignal(
            action="BUY",
            side="YES",
            quantity=10,
            price=market_state.yes_price
        )
    return None
    

engine = BacktestEngine(initial_capital=100000)
output = engine.run(start_ts=1765585170, end_ts=1766017170, interval=None, strategy=strategyRando, date="december-19", ffill=True, free=False)

snapshots_to_df(output)
