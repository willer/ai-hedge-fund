#!/usr/bin/env python
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Run the AI Hedge Fund with default settings")
    parser.add_argument("tickers", type=str, nargs="?", default="AAPL,MSFT,NVDA,GOOGL,META,AMZN", 
                        help="Comma-separated list of stock ticker symbols (default: AAPL,MSFT,NVDA,GOOGL,META,AMZN)")
    parser.add_argument("--tickers", type=str, dest="tickers_opt",
                        help="Alternative way to specify tickers (comma-separated)")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--show-reasoning", action="store_true", help="Show reasoning from each agent")
    
    args = parser.parse_args()
    
    # Use --tickers if provided, otherwise use positional argument
    tickers = args.tickers_opt if args.tickers_opt else args.tickers
    
    cmd = ["python", "src/main.py", "--tickers", tickers]
    
    if args.start_date:
        cmd.extend(["--start-date", args.start_date])
    
    if args.end_date:
        cmd.extend(["--end-date", args.end_date])
    
    if args.show_reasoning:
        cmd.append("--show-reasoning")
    
    print(f"Running hedge fund with tickers: {tickers}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
