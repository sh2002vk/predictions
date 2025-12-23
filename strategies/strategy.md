TODO's and notes

- a strategy should be able to return multiple trade signals

- a strategy should be able to tell, where within the timeframe of the run, its being called, like is it early in, or later in
    - for example, if the strategy is that a strong leader in the start of a market, say 70% confidence or above, will ALWAYS be final #1 app, that should be possible by checking how long its been since the start of the market/run

- there should be a way for the the engine to determine what the final outcome is of ACTIVE trades, AFTER the timeframe of the run is completed. Because currently its only looking at the movement in price of contracts, not the final close and how that would affect pnl. Otherwise, the backtest should be closing out all trades before it completes

- it should be able to look at the previous signals it sent, and see if anything should be closed
    - the close operation needs to be more refined, and double check the engine can support and is logically correct