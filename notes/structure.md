## Design v1

The overall modules that play here are:
- Market Data (Live information)
- State Manager (Portfolio view)
- Strategy & Execution (Trading)
- Metrics (Review)

### Market Data
Files included:
- app_store_connector.py
- polymarket_connector.py

Continuously poll and normalize data into readable views

### State Manager
Establish state for:
- liquidity
- current positions
- time

### Strategy & Execution
Layer that reviews and deploys strategies
Need to refine

Create signals on data collected and execute on them

### Metrics
Clean up and update ledger

## Flow
- Pull live data 
- Update ledger state
- Execute signal construction and execute
- Clean up movements

Step 1:
Complete a live ledger state