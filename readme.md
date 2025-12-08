# How to use
Set up your venv, and then use engine.py as the entrypoint.

Specifics on how the *current* structure of this system is build, is in structure.md.

# Strategies

## Strategy1
This attempts to find top of book arbitrage. Prelim tests show polymarket is too efficient for this type of arb to exist.
  - if ASK_YES + ASK_NO < 1 then BUY. Because your payout will be 1, so profit (1 - (ASK_YES + ASK_NO)) > 0 
  - if ASK_YES + ASK_NO >= 1 then DO NOT BUY. Because then profit (1 - (ASK_YES + ASK_NO)) < 0
  - if BID_YES + BID_NO > 1 then SELL. Because your profit will be ((BID_YES + BID_NO) - 1) > 0
  - if BID_YES + BID_NO <= 1 then DO NOT SELL. Because your profit will be ((BID_YES + BID_NO) - 1) < 0

#### To install
```pipenv install --dev```

#### To execute 
```
pipenv shell
python strategy1.py
```

#### Next Steps for S2
- Look deeper, accounting for both size and price to find the best ask/bid in a given yes/no
- Start factoring in trading fees and gas 
- Explore other types of arbitrage

# Current Focus
Work on the flow, how its going to actually interact with the data coming in, how to design, deploy and test new trading strategies.
Also note that currently its operating under paper money

