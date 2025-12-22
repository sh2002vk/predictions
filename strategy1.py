# USE TO MESS AROUND

# WARNING: This is probably out of date after refactoring changes

from polymarket_connector import *


def arbStrategy1(yesOrderBook, noOrderBook):
    """
    STRATEGY 1

    This strategy is looking for order book arbitrage, withing a single prediction in a given market.

    4 values to focus on are:
        ASK_YES
        ASK_NO
        BID_YES
        BID_NO

    if ASK_YES + ASK_NO < 1 then BUY. Because your payout will be 1, so profit (1 - (ASK_YES + ASK_NO)) > 0
    if ASK_YES + ASK_NO >= 1 then DO NOT BUY. Because then profit (1 - (ASK_YES + ASK_NO)) < 0
    if BID_YES + BID_NO > 1 then SELL. Because your profit will be ((BID_YES + BID_NO) - 1) > 0
    if BID_YES + BID_NO <= 1 then DO NOT SELL. Because your profit will be ((BID_YES + BID_NO) - 1) < 0

    MESSY FUNCTION, CLEAN THIS UP LATER. BUT LOOKS LIKE, POLYMARKET IS TOO EFFICIENT FOR THIS TYPE OF ARB.
    Next steps:
    - Look deeper, accounting for both size and price to find the best ask/bid in a given yes/no
    - Explore other types of arbitrage

    :param yesOrderBook, noOrderBook:
    :return:
    """

    # find best ask yes
    # find best ask no
    # chose the min contract size between best ask yes, best ask no
    # optimization: have the ability to update the best yes/no if there is more profit for a lower price because of a
    # larger size
    best_ask_yes = {"price": float('inf'), "size": 0.0}
    best_ask_no = {"price": float('inf'), "size": 0.0}
    for ask in yesOrderBook.asks:
        if float(ask.price) < best_ask_yes["price"]:
            best_ask_yes["price"] = float(ask.price)
            best_ask_yes["size"] = float(ask.size)
    for ask in noOrderBook.asks:
        if float(ask.price) < best_ask_no["price"]:
            best_ask_no["price"] = float(ask.price)
            best_ask_no["size"] = float(ask.size)
    max_order_size = min(best_ask_yes["size"], best_ask_no["size"])
    sum_value_asks = best_ask_yes["price"] + best_ask_no["price"]
    if sum_value_asks < 1:
        print(f"FOUND ARB -- ASKS -- sum: {sum_value_asks}, order size: {max_order_size}")
        raise ValueError("READ THE DATA")
    else:
        print(f"NO ARB -- ASKS -- sum: {sum_value_asks}, order size: {max_order_size}")


    # find best bid yes
    # find best bid no
    best_bid_yes = {"price": 0.0, "size": 0.0}
    best_bid_no = {"price": 0.0, "size": 0.0}
    for bid in yesOrderBook.bids:
        if float(bid.price) > best_bid_yes["price"]:
            best_bid_yes["price"] = float(bid.price)
            best_bid_yes["size"] = float(bid.size)
    for bid in noOrderBook.bids:
        if float(bid.price) > best_bid_no["price"]:
            best_bid_no["price"] = float(bid.price)
            best_bid_no["size"] = float(bid.size)
    max_order_size = min(best_bid_yes["size"], best_bid_no["size"])
    sum_value_bids = best_bid_yes["price"] + best_bid_no["price"]
    if sum_value_bids > 1:
        print(f"FOUND ARB -- BIDS -- sum: {sum_value_bids}, order size: {max_order_size}")
        raise ValueError("READ THE DATA")
    else:
        print(f"NO ARB -- BIDS -- sum: {sum_value_bids}, order size: {max_order_size}")

    return


while True:
    dateSlug = "december-12"

    bets = fetchBetsForDate(dateSlug)
    orderBookClient = OrderBook()

    for bet in bets:
        yesClobToken = bet["yesClobToken"]
        noClobToken = bet["noClobToken"]
        yesOrderBook = orderBookClient.getOrderBook(tokenId=yesClobToken)
        noOrderBook = orderBookClient.getOrderBook(tokenId=noClobToken)
        arbStrategy1(yesOrderBook=yesOrderBook, noOrderBook=noOrderBook)
