from typing import List, Dict, Optional, Tuple, Union
import json
import re

def parse_candidate_name(question: str) -> Optional[str]:
    """
    Extracts candidate name from election market questions.
    Handles formats like:
    - "Will Stephen A. Smith win the 2028 Democratic presidential nomination?"
    - "Will [Candidate] win the [Year] [Party] presidential nomination?"
    """
    # Pattern: "Will [Name] win..."
    match = re.match(r"^Will\s+(.+?)\s+win\b", question)
    if match:
        return match.group(1).strip()
    return None

def parse_outcome_prices(raw: Union[str, list]) -> Optional[Tuple[float, float]]:
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

def parse_election_markets(markets: List[Dict]) -> List[Dict]:
    """
    Parses election market data from Polymarket API.
    
    Args:
        markets: List of market dictionaries from Polymarket API
    
    Returns:
        List of parsed election market dictionaries with structured data
    """
    parsed_markets = []

    for market in markets:
        outcome_prices_raw = market.get("outcomePrices")
        parsed_prices = parse_outcome_prices(outcome_prices_raw)

        # Skip markets where outcomePrices are missing or invalid
        if parsed_prices is None:
            continue

        if not market.get("clobTokenIds"):
            continue
        
        clobTokenIds = json.loads(market.get("clobTokenIds"))
        yes_outcome_price, no_outcome_price = parsed_prices

        parsed_market = {
            "candidate": parse_candidate_name(market.get("question", "")),
            "question": market.get("question", ""),
            "startDate": market.get("startDate"),
            "endDate": market.get("endDate"),
            "liquidity": market.get("liquidity"),
            "volume": market.get("volume"),
            "active": market.get("active"),
            "volumeNum": market.get("volumeNum"),
            "yesOutcome": yes_outcome_price,
            "noOutcome": no_outcome_price,
            "yesClobToken": clobTokenIds[0],
            "noClobToken": clobTokenIds[1],
            "conditionId": market.get("conditionId"),
            "slug": market.get("slug"),
            # Include other useful fields
            "bestBid": market.get("bestBid"),
            "bestAsk": market.get("bestAsk"),
            "lastTradePrice": market.get("lastTradePrice"),
        }
        parsed_markets.append(parsed_market)

    return parsed_markets

