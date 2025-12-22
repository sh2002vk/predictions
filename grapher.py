import pandas as pd
import matplotlib.pyplot as plt

def snapshots_to_df(output):
    snaps = output["snapshots"]
    if not snaps:
        raise ValueError("No snapshots to plot (snapshots list is empty).")

    df = pd.DataFrame([{
        "timestamp": s.timestamp,
        "liquid_value": s.liquid_value,
        "unrealized_pnl": s.unrealized_pnl,
        "total_value": s.total_value,
        "num_active_trades": s.num_active_trades
    } for s in snaps])

    df = df.sort_values("timestamp")
    df["dt"] = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.tz_convert("America/Vancouver")
    
    plt.figure()
    plt.plot(df["dt"], df["total_value"])
    plt.title("Backtest Total Value (Equity Curve)")
    plt.xlabel("Time")
    plt.ylabel("Total Value")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

    # 2) Cash vs unrealized PnL
    plt.figure()
    plt.plot(df["dt"], df["liquid_value"], label="Cash (LiquidValue)")
    plt.plot(df["dt"], df["unrealized_pnl"], label="Unrealized PnL")
    plt.title("Cash and Unrealized PnL Over Time")
    plt.xlabel("Time")
    plt.ylabel("USD")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

    # 3) Active trades count
    plt.figure()
    plt.plot(df["dt"], df["num_active_trades"])
    plt.title("Active Trades Over Time")
    plt.xlabel("Time")
    plt.ylabel("# Active Trades")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

