import requests
import json

from typing import List, Dict, Optional, Tuple, Union
from py_clob_client.client import ClobClient
from market_parsers.app_store_rankings import parse_app_rankings
from dataclasses import dataclass

@dataclass
class PriceHistoryInterval:
    MAX = "max"
    ONE_WEEK = "1w"
    ONE_DAY = "1d"
    SIX_HOURS = "6h"
    ONE_HOUR = "1h"           # interval of the price history

@dataclass
class MarketPrice:
    t: int          # timestamp
    p: float        # price in $


class PolymarketConnector:
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com/events/slug"  # public endpoint to get market data
        self.free_apps = "1-free-app-in-the-us-apple-app-store-on-"     # slug of market, move to constants later
        self.paid_apps = "1-paid-app-in-the-us-apple-app-store-on-"     # slug of market, move to constants later
    
    def get_app_store_rankings(self, free: bool, date: str):
        # free -> if true is free if false is paid
        if free:
            slug = f"{self.free_apps}{date}"
        else: 
            slug = f"{self.paid_apps}{date}"
        url = f"{self.base_url}/{slug}"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        print('got data response back')
        with open('test.json', 'w') as file:
            json.dump(data, file)
        markets = data.get("markets", [])
        bets = parse_app_rankings(markets)
        return bets


class OrderBook:
    def __init__(self):
        self.host = "https://clob.polymarket.com"
        self.chain_id = 137

        self.client = ClobClient(
            host=self.host,
            chain_id=self.chain_id
        )

    def get_order_book(self, tokenId):
        # tokenId = CLOB (order book) token ID
        orderBook = self.client.get_order_book(tokenId)
        return orderBook

    def get_historical_prices(self, order_book_params: dict):
       # Fetches the historical prices for the given parameters
        url = f"{self.host}/prices-history"
        response = requests.get(url, params=order_book_params)
        return json.loads(response.text)



