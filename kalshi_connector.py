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
        return data

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
        #tickers is specific market tickers, passed in as a comma separated list
        url = f"{self.base_url}/markets"
        payload = {}
        
        if event_ticker is not None:
            payload["event_ticker"] = event_ticker
        if series_ticker is not None:
            payload["series_ticker"] = series_ticker
        if status is not None:
            payload["status"] = status
        if tickers is not None:
            payload["tickers"] = tickers

        url = f"{self.base_url}/markets"
        response = requests.get(url, json=payload)
        print(response)
        data = response.json()
        return data


k = KalshiConnector()
# print(k.get_trading_status())
# print(k.get_series("KXHIGHNY"))
# print(k.get_specific_market_data("kxhighchi-26jan22"))
print(k.get_markets_for_event("kxhighchi-26jan23"))
# print(k.get_markets(series_ticker="KXHIGHNY", status=None))




# # import requests

# url = "https://api.elections.kalshi.com/trade-api/v2/markets?limit=1&series_ticker=KXHIGHCHI"

# response = requests.get(url)

# print(response.json())



# {'cursor': 'CgwI3fjHywYQyPfp1QESFEtYSElHSENISS0yNkpBTjIzLVQ1', 'markets': [{'can_close_early': True, 'cap_strike': 5, 'close_time': '2026-01-24T05:59:00Z', 'created_time': '2026-01-22T10:30:53.448429Z', 'early_close_condition': 'The Last Trading Time will be 11:59 PM ET on January 23, 2026 regardless of any data releases or events occurring. Expiration will occur on the sooner of the first 7:00 or 8:00\nAM ET following the release of the data for January 23, 2026, or one week after January 23, 2026.', 'event_ticker': 'KXHIGHCHI-26JAN23', 'expected_expiration_time': '2026-01-24T15:00:00Z', 'expiration_time': '2026-01-30T15:00:00Z', 'expiration_value': '', 'last_price': 27, 'last_price_dollars': '0.2700', 'latest_expiration_time': '2026-01-30T15:00:00Z', 'liquidity': 271886, 'liquidity_dollars': '2718.8600', 'market_type': 'binary', 'no_ask': 74, 'no_ask_dollars': '0.7400', 'no_bid': 73, 'no_bid_dollars': '0.7300', 'no_sub_title': '4° or below', 'notional_value': 100, 'notional_value_dollars': '1.0000', 'open_interest': 2680, 'open_interest_fp': '2680.00', 'open_time': '2026-01-22T15:00:00Z', 'previous_price': 0, 'previous_price_dollars': '0.0000', 'previous_yes_ask': 0, 'previous_yes_ask_dollars': '0.0000', 'previous_yes_bid': 0, 'previous_yes_bid_dollars': '0.0000', 'price_level_structure': 'linear_cent', 'price_ranges': [{'end': '1.0000', 'start': '0.0000', 'step': '0.0100'}], 'response_price_units': 'usd_cent', 'result': '', 'rules_primary': "If the highest temperature recorded at Chicago Midway, IL for January 23, 2026, is less than 5° according to the National Weather Service's Climatological Report (Daily), then the market resolves to Yes.", 'rules_secondary': 'Not all weather data is the same. While checking a source like AccuWeather or Google Weather may help guide your decision, the official and final value used to determine this market is the highest temperature as reported by the corresponding NWS Climatological Report (Daily) linked in the rules above. Preliminary NWS reporting and measurement methods may be subject to underlying rounding and conversion nuances. Traders should exercise caution when interpreting preliminary NWS data.', 'settlement_timer_seconds': 3600, 'status': 'active', 'strike_type': 'less', 'subtitle': '4° or below', 'tick_size': 1, 'ticker': 'KXHIGHCHI-26JAN23-T5', 'title': 'Will the high temp in Chicago be <5° on Jan 23, 2026?', 'volume': 4316, 'volume_24h': 4302, 'volume_24h_fp': '4302.00', 'volume_fp': '4316.00', 'yes_ask': 27, 'yes_ask_dollars': '0.2700', 'yes_bid': 26, 'yes_bid_dollars': '0.2600', 'yes_sub_title': '4° or below'}]}