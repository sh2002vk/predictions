# Polymarket Trading

## Table of Contents
1. [Setup](#setup)
2. [Backtesting Engine](#backtesting-engine)
3. [Strategies](#strategies)

## Setup
Install pipenv and then use `engine.py` as the entrypoint.
```
pipenv install --dev
```

Specifics on how the *current* structure of this system is built is in [structure.md](/notes/structure.md).

## Backtesting Engine
Note: please go to [/strategies](/strategies/) after to see a todo list of improvements to implement and notes

In `backtestEngine.py`:
- `price_panel`: the df that contains records from start to end of t, token, no, yes, ticker, yes_token, no_token with timestamp and token as the index
- The strategy should be passed in, as a *callable* parameter
- Currently, there is a random strategy that generates buy signals, to test out the backtesting system
- At the end, it also graphs the output of the backtest run. 

In the virtual environment, run `python backtestEngine.py` to try out a random strategy

## Strategies
Work on the flow, how its going to actually interact with the data coming in, how to design, deploy and test new trading strategies.
Also note that currently its operating under paper money

### Strategy1
This attempts to find top of book arbitrage. Prelim tests show polymarket is too efficient for this type of arb to exist.
  - if `ASK_YES + ASK_NO < 1` then `BUY`. Because your payout will be 1, so profit `(1 - (ASK_YES + ASK_NO)) > 0`
  - if `ASK_YES + ASK_NO >= 1` then `DO NOT BUY`. Because then profit `(1 - (ASK_YES + ASK_NO)) < 0`
  - if `BID_YES + BID_NO > 1` then `SELL`. Because your profit will be `((BID_YES + BID_NO) - 1) > 0`
  - if `BID_YES + BID_NO <= 1` then `DO` NOT SELL. Because your profit will be `((BID_YES + BID_NO) - 1) < 0`

### Next Steps for S2
- Look deeper, accounting for both size and price to find the best ask/bid in a given yes/no
- Start factoring in trading fees and gas 
- Explore other types of arbitrage
