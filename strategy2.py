## STRATEGY 3

# This strategy is looking for order book arbitrage, within the same market but across predictions. 

# e.g. Market is #1 App Store app, 
# shadow rocket yes contract is functionally equivalent to hot schedules no contract

# 2 values to focus on are:
#     ASK_YES
#     ASK_NO

# if sum(ASK_YES) across all predictions < 1 then BUY. Because your payout will be 1, so profit (1 - sum(ASK_YES)) > 0
# if sum(ASK_NO) across all predictions < 1 then BUY. Because your payout will be 1, so profit (1 - sum(ASK_NO)) > 0


from polymarket_connector import PolymarketConnector, OrderBook
from market_parsers.election_markets import parse_election_markets

connector = PolymarketConnector()
order_book_client = OrderBook()


def get_parsed_markets():
    raw_markets = connector.get_markets_from_slug("democratic-presidential-nominee-2028")
    parsed_markets = parse_election_markets(raw_markets)
    print(f"Total candidates: {len(parsed_markets)}")
    return parsed_markets


def get_best_prices(parsed_markets):
    # Get best ask prices from order books
    best_yes_asks = []
    best_no_asks = []
    candidates_with_data = []

    for market in parsed_markets:
        candidate = market.get('candidate', 'Unknown')
        yes_token = market.get('yesClobToken')
        no_token = market.get('noClobToken')
        
        if not yes_token or not no_token:
            continue
        
        try:
            # Get order books
            yes_order_book = order_book_client.get_order_book(yes_token)
            no_order_book = order_book_client.get_order_book(no_token)
            
            # Find best (lowest) ask price for YES
            best_yes_ask = float('inf')
            best_yes_size = 0.0
            if yes_order_book.asks:
                for ask in yes_order_book.asks:
                    ask_price = float(ask.price)
                    if ask_price < best_yes_ask:
                        best_yes_ask = ask_price
                        best_yes_size = float(ask.size)
            
            # Find best (lowest) ask price for NO
            best_no_ask = float('inf')
            best_no_size = 0.0
            if no_order_book.asks:
                for ask in no_order_book.asks:
                    ask_price = float(ask.price)
                    if ask_price < best_no_ask:
                        best_no_ask = ask_price
                        best_no_size = float(ask.size)
            
            if best_yes_ask != float('inf'):
                best_yes_asks.append({
                    'candidate': candidate,
                    'price': best_yes_ask,
                    'size': best_yes_size
                })
            
            if best_no_ask != float('inf'):
                best_no_asks.append({
                    'candidate': candidate,
                    'price': best_no_ask,
                    'size': best_no_size
                })
            
            candidates_with_data.append(candidate)
            
        except Exception as e:
            print(f"Error fetching order book for {candidate}: {e}")
            continue

    print(f"\nSuccessfully fetched order books for {len(candidates_with_data)} candidates")

    return best_yes_asks, best_no_asks


def arbitrage_check(parsed_markets, best_yes_asks, best_no_asks):
    sum_best_yes_asks = sum(item['price'] for item in best_yes_asks)
    sum_best_no_asks = sum(item['price'] for item in best_no_asks)

    # Also get current mid prices for comparison
    sum_current_yes_prices = sum(market['yesOutcome'] for market in parsed_markets)
    sum_current_no_prices = sum(market['noOutcome'] for market in parsed_markets)


    print(f"Current YES prices (mid-market): {sum_current_yes_prices:.6f}")
    print(f"Best YES ask prices (actual buy cost): {sum_best_yes_asks:.6f}")
    print(f"\nCurrent NO prices (mid-market): {sum_current_no_prices:.6f}")
    print(f"Best NO ask prices (actual buy cost): {sum_best_no_asks:.6f}")

    print("\n" + "-"*60)
    print("ARBITRAGE CHECK")
    print("-"*60)

    # Check YES arbitrage
    if sum_best_yes_asks < 1.0:
        
        # Find minimum size available (bottleneck)
        min_size_item = min(best_yes_asks, key=lambda x: x['size'])
        min_size = min_size_item['size']
        limiting_candidate = min_size_item['candidate']

        profit_per_contract = 1.0 - sum_best_yes_asks
        profit_pct = (profit_per_contract / sum_best_yes_asks) * 100

        
        # Calculate actual profit with fractional contracts
        # You buy min_size contracts for EACH candidate
        total_cost = sum_best_yes_asks * min_size  # Cost to buy min_size contracts for each candidate
        guaranteed_payout = min_size  # One candidate wins, pays out min_size
        actual_profit = guaranteed_payout - total_cost
        
        print(f"POTENTIAL YES-order ARBITRAGE FOUND!")
        print(f"Cost per contract set: ${sum_best_yes_asks:.6f}")
        print(f"Profit per contract: ${profit_per_contract:.6f} ({profit_pct:.2f}%)")
        print(f"Note: This does NOT account for trading fees")
        print(f"\n   Execution Details:")
        print(f"Maximum contracts per candidate: {min_size:.2f} contracts")
        print(f"Limiting factor: {limiting_candidate} (only {min_size:.2f} contracts available)")
        print(f"Total cost: ${total_cost:.6f} (${sum_best_yes_asks:.6f} × {min_size:.2f})")
        print(f"Guaranteed payout: ${guaranteed_payout:.6f} (one candidate will win)")
        print(f"Net profit (before fees): ${actual_profit:.6f}")
        if total_cost > 0:
            print(f"Profit percentage: {(actual_profit / total_cost * 100):.2f}%")
    else:
        print(f"NO YES-order ARBITRAGE")
        print(f"Cost to buy all YES contracts: ${sum_best_yes_asks:.6f}")
        print(f"This exceeds $1.00, so no arbitrage opportunity")


def main():
    parsed_markets = get_parsed_markets()
    best_yes_asks, best_no_asks = get_best_prices(parsed_markets)
    arbitrage_check(parsed_markets, best_yes_asks, best_no_asks)

main()