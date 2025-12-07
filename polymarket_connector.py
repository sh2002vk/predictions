import requests
import json
import re
from typing import List, Dict, Optional, Tuple, Union
from py_clob_client.client import ClobClient


BASE_URL = "https://gamma-api.polymarket.com/events/slug"


def parseName(question: str) -> Optional[str]:
    match = re.match(r"^Will\s+(.+?)\s+be\b", question)
    if match:
        return match.group(1).strip()
    return None


def parseOutcomePrices(raw: Union[str, list]) -> Optional[Tuple[float, float]]:
    """
    Takes outcomePrices, which can be:
      - a JSON string like '["0.865", "0.135"]'
      - or already a list like ["0.865", "0.135"]
    Returns a tuple of floats: (yes_price, no_price)
    """
    # If it's a string, parse JSON first
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None

    # Now expect a list-like structure with at least 2 entries
    if not isinstance(raw, (list, tuple)) or len(raw) < 2:
        return None

    try:
        yes = float(raw[0])
        no = float(raw[1])
        return yes, no
    except (ValueError, TypeError):
        return None


def buildSlug(date_slug: str) -> str:
    return f"1-free-app-in-the-us-apple-app-store-on-{date_slug}"


def fetchBetsForDate(date_slug: str) -> List[Dict]:
    """
    Central function:
    - Takes a date slug, e.g. 'november-28'
    - Builds the event slug
    - Calls the Polymarket API
    - Returns a list of bet dicts
    """
    slug = buildSlug(date_slug)
    url = f"{BASE_URL}/{slug}"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    markets = data.get("markets", [])
    bets: List[Dict] = []

    for market in markets:
        outcome_prices_raw = market.get("outcomePrices")
        parsed_prices = parseOutcomePrices(outcome_prices_raw)

        # Skip markets where outcomePrices are missing or invalid
        if parsed_prices is None:
            continue

        print(f"\n{market}")

        yes_outcome_price, no_outcome_price = parsed_prices

        bet = {
            "app": parseName(market.get("question", "")),
            "startDate": market.get("startDate"),
            "endDate": market.get("endDate"),
            "liquidity": market.get("liquidity"),
            "volume": market.get("volume"),
            "active": market.get("active"),
            "volumeNum": market.get("volumeNum"),
            "yesOutcome": yes_outcome_price,
            "noOutcome": no_outcome_price,
            "yesClobToken": market.get("clobTokenIds")[0],
            "noClobToken": market.get("clobTokenIds")[1]
        }
        bets.append(bet)

    return bets


class OrderBook:
    def __init__(self):
        self.host = "https://clob.polymarket.com"
        self.chain_id = 137

        self.client = ClobClient(
            host=self.host,
            chain_id=self.chain_id
        )

    async def getOrderBook(self, tokenId):
        """ tokenId = CLOB (order book) token ID
        Remember that:
            bid = sell
            ask = buy
        """
        orderBook = await self.client.getOrderBook(tokenId=tokenId)
        print(orderBook)

        # for i in orderBook["bids"]:
        #     print(f"Bid: {i}")
        #
        # for i in orderBook["asks"]:
        #     print(f"Ask: {i}")



