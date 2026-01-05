from polymarket_connector import PolymarketConnector, OrderBook
from market_parsers.election_markets import parse_election_markets

connector = PolymarketConnector()

# Fetch raw markets from election market
raw_markets = connector.get_markets_from_slug("democratic-presidential-nominee-2028")

# Parse the markets using the election parser
parsed_markets = parse_election_markets(raw_markets)

# Now you have structured data
# for market in parsed_markets:
#     print(f"Candidate: {market['candidate']}")
#     print(f"YES Price: {market['yesOutcome']:.4f}")
#     print(f"NO Price: {market['noOutcome']:.4f}")
#     print(f"YES Token: {market['yesClobToken']}")
#     print(f"NO Token: {market['noClobToken']}")
#     print(f"Volume: {market.get('volumeNum', 'N/A')}")
#     print("---")

print(len(parsed_markets))

#get sum of YES prices
sum_of_yes_prices = sum(market['yesOutcome'] for market in parsed_markets)
print(f"Sum of YES prices: {sum_of_yes_prices:.4f}")

#get sum of NO prices
sum_of_no_prices = sum(market['noOutcome'] for market in parsed_markets)
print(f"Sum of NO prices: {sum_of_no_prices:.4f}")