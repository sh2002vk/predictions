import requests
import json

# from typing import List, Dict, Optional, Tuple, Union
# from py_clob_client.client import ClobClient
# from market_parsers.app_store_rankings import parse_app_rankings
# from dataclasses import dataclass


class KalshiConnector:
    def __init__(self):
        self.base_url = "https://api.elections.kalshi.com/trade-api/v2" # this is unauthenticated endpoint
        # self.api_key = os.getenv("KALSHI_API_KEY")

    def get_trading_status(self):
        #gets the status of the exchange to see if trading is active
        url = f"{self.base_url}/exchange/status"
        response = requests.get(url)
        data = response.json()
        trading_active = data["trading_active"]
        return trading_active

    def get_series(self, series_ticker: str):
        url = f"{self.base_url}/series/{series_ticker}"
        response = requests.get(url)
        data = response.json()
        return data

    def get_markets_for_series(self, series_ticker: str):
        url = f"{self.base_url}/markets?series_ticker={series_ticker}&status=open"
        response = requests.get(url)
        data = response.json()

        # Extract markets from the response (Kalshi returns {'markets': [...], 'cursor': '...'})
        markets_list = data.get('markets', [])
        
        # Filter out any error dictionaries and extract clean market data
        markets_clean = [
            {
                'ticker': m.get('ticker'),
                'title': m.get('title'),
                'event_ticker': m.get('event_ticker'),
                'yes_bid': m.get('yes_bid'),
                'yes_ask': m.get('yes_ask'),
                'no_bid': m.get('no_bid'),
                'no_ask': m.get('no_ask'),
                'last_price': m.get('last_price'),
                'last_price_dollars': m.get('last_price_dollars'),
                'status': m.get('status'),
                'open_time': m.get('open_time'),
                'close_time': m.get('close_time')
            }
            for m in markets_list
            if isinstance(m, dict) and 'ticker' in m and 'error' not in m
        ]

        return markets_clean

    def get_markets_for_event(self, event_ticker: str):
        url = f"{self.base_url}/events/{event_ticker}/metadata"
        response = requests.get(url)
        data = response.json()
        market_data = data['market_details']
        return data


    def get_specific_market_data(self, ticker: str):
        url = f"{self.base_url}/markets/{ticker}"
        response = requests.get(url)
        data = response.json()

        return data

    def get_markets(self, limit=100, event_ticker=None, series_ticker=None, status='open', tickers=None):
        """
        Abstracted function for retrieving market data from Kalshi API based on flexible filtering criteria.
        
        This method allows you to query markets using various combinations of filters. All parameters are optional
        and can be combined to narrow down the results. The function returns a cleaned list of market dictionaries
        with essential market information.
        
        Args:
            limit (int, optional): Maximum number of markets to return. Defaults to 100.
            event_ticker (str, optional): Filter markets by a specific event ticker (e.g., 'KXHIGHCHI-26JAN30').
            series_ticker (str, optional): Filter markets by a specific series ticker (e.g., 'KXHIGHCHI').
            status (str, optional): Filter markets by status. Common values: 'open', 'closed', 'settled'. 
                                    Defaults to 'open'. Pass None to get all statuses.
            tickers (str, optional): Comma-separated list of specific market tickers to retrieve.
        
        Returns:
            list: A list of dictionaries, each containing cleaned market data with the following keys:
                - ticker: Market ticker identifier
                - title: Market title/question
                - event_ticker: Associated event ticker
                - yes_bid: Yes side bid price (in cents)
                - yes_ask: Yes side ask price (in cents)
                - no_bid: No side bid price (in cents)
                - no_ask: No side ask price (in cents)
                - last_price: Last traded price (in cents)
                - last_price_dollars: Last traded price (in dollars)
                - status: Market status
                - open_time: Market open time (ISO format)
                - close_time: Market close time (ISO format)
        
        Examples:
            # Get all open markets in a series
            markets = connector.get_markets(series_ticker='KXHIGHCHI', status='open')
            
            # Get markets for a specific event
            markets = connector.get_markets(event_ticker='KXHIGHCHI-26JAN30')
            
            # Get specific markets by ticker
            markets = connector.get_markets(tickers='KXHIGHCHI-26JAN30-T23,KXHIGHCHI-26JAN30-T24')
            
            # Get all markets (any status) with a limit
            markets = connector.get_markets(limit=50, status=None)
        """
        #tickers is specific market tickers, passed in as a comma separated list
        url = f"{self.base_url}/markets"
        params = {}
        
        if limit is not None:
            params["limit"] = limit
        if event_ticker is not None:
            params["event_ticker"] = event_ticker
        if series_ticker is not None:
            params["series_ticker"] = series_ticker
        if status is not None:
            params["status"] = status
        if tickers is not None:
            params["tickers"] = tickers

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        markets_list = data.get('markets', [])
        
        # Filter out any error dictionaries and extract clean market data
        markets_clean = [
            {
                'ticker': m.get('ticker'),
                'title': m.get('title'),
                'event_ticker': m.get('event_ticker'),
                'yes_bid': m.get('yes_bid'),
                'yes_ask': m.get('yes_ask'),
                'no_bid': m.get('no_bid'),
                'no_ask': m.get('no_ask'),
                'last_price': m.get('last_price'),
                'last_price_dollars': m.get('last_price_dollars'),
                'status': m.get('status'),
                'open_time': m.get('open_time'),
                'close_time': m.get('close_time')
            }
            for m in markets_list
            if isinstance(m, dict) and 'ticker' in m and 'error' not in m
        ]

        return markets_clean


k = KalshiConnector()
# print(k.get_markets_for_series('KXHIGHCHI'))
# print(k.get_trading_status())
# print(k.get_series("KXHIGHNY"))
# print(k.get_specific_market_data("kxhighchi-26jan29"))
# print(k.get_markets_for_event("kxhighchi-26jan23"))
print(k.get_markets(series_ticker="KXHIGHCHI", status='open'))




# # import requests

# url = "https://api.elections.kalshi.com/trade-api/v2/markets?limit=1&series_ticker=KXHIGHCHI"

# response = requests.get(url)

# print(response.json())



# {'cursor': 'CgwI3fjHywYQyPfp1QESFEtYSElHSENISS0yNkpBTjIzLVQ1', 'markets': [{'can_close_early': True, 'cap_strike': 5, 'close_time': '2026-01-24T05:59:00Z', 'created_time': '2026-01-22T10:30:53.448429Z', 'early_close_condition': 'The Last Trading Time will be 11:59 PM ET on January 23, 2026 regardless of any data releases or events occurring. Expiration will occur on the sooner of the first 7:00 or 8:00\nAM ET following the release of the data for January 23, 2026, or one week after January 23, 2026.', 'event_ticker': 'KXHIGHCHI-26JAN23', 'expected_expiration_time': '2026-01-24T15:00:00Z', 'expiration_time': '2026-01-30T15:00:00Z', 'expiration_value': '', 'last_price': 27, 'last_price_dollars': '0.2700', 'latest_expiration_time': '2026-01-30T15:00:00Z', 'liquidity': 271886, 'liquidity_dollars': '2718.8600', 'market_type': 'binary', 'no_ask': 74, 'no_ask_dollars': '0.7400', 'no_bid': 73, 'no_bid_dollars': '0.7300', 'no_sub_title': '4° or below', 'notional_value': 100, 'notional_value_dollars': '1.0000', 'open_interest': 2680, 'open_interest_fp': '2680.00', 'open_time': '2026-01-22T15:00:00Z', 'previous_price': 0, 'previous_price_dollars': '0.0000', 'previous_yes_ask': 0, 'previous_yes_ask_dollars': '0.0000', 'previous_yes_bid': 0, 'previous_yes_bid_dollars': '0.0000', 'price_level_structure': 'linear_cent', 'price_ranges': [{'end': '1.0000', 'start': '0.0000', 'step': '0.0100'}], 'response_price_units': 'usd_cent', 'result': '', 'rules_primary': "If the highest temperature recorded at Chicago Midway, IL for January 23, 2026, is less than 5° according to the National Weather Service's Climatological Report (Daily), then the market resolves to Yes.", 'rules_secondary': 'Not all weather data is the same. While checking a source like AccuWeather or Google Weather may help guide your decision, the official and final value used to determine this market is the highest temperature as reported by the corresponding NWS Climatological Report (Daily) linked in the rules above. Preliminary NWS reporting and measurement methods may be subject to underlying rounding and conversion nuances. Traders should exercise caution when interpreting preliminary NWS data.', 'settlement_timer_seconds': 3600, 'status': 'active', 'strike_type': 'less', 'subtitle': '4° or below', 'tick_size': 1, 'ticker': 'KXHIGHCHI-26JAN23-T5', 'title': 'Will the high temp in Chicago be <5° on Jan 23, 2026?', 'volume': 4316, 'volume_24h': 4302, 'volume_24h_fp': '4302.00', 'volume_fp': '4316.00', 'yes_ask': 27, 'yes_ask_dollars': '0.2700', 'yes_bid': 26, 'yes_bid_dollars': '0.2600', 'yes_sub_title': '4° or below'}]}




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