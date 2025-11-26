#!/usr/bin/env python
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Run the AI Hedge Fund Backtester with default settings")
    parser.add_argument("tickers", type=str, nargs="?", default="AAPL,MSFT,NVDA,GOOGL",
                        help="Comma-separated list of stock ticker symbols (default: AAPL,MSFT,NVDA,GOOGL)")
    parser.add_argument("--tickers", type=str, dest="tickers_opt",
                        help="Alternative way to specify tickers (comma-separated)")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")

    args = parser.parse_args()
    
    # Use --tickers if provided, otherwise use positional argument
    tickers = args.tickers_opt if args.tickers_opt else args.tickers
    
    cmd = ["python", "src/backtester.py", "--tickers", tickers]
    
    if args.start_date:
        cmd.extend(["--start-date", args.start_date])
    
    if args.end_date:
        cmd.extend(["--end-date", args.end_date])
    
    print(f"Running backtester with tickers: {tickers}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
