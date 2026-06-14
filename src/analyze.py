import pandas as pd
import yfinance as yf
from datetime import datetime
from tabulate import tabulate
from stockstats import StockDataFrame
import numpy as np
import os

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

RSI_STRONG_OVERSOLD = 37
RSI_MILD_CORRECTION = 45
RSI_NEUTRAL_MAX = 58
RSI_EXPENSIVE = 63

DB_FILE = 'my_etf.csv'
LAST_RATE_FILE = "last_eur_usd.txt"

# Cache for yfinance data: key = (tuple(tickers), period)
_data_cache = {}

def fetch_etf_data(tickers, period="6mo"):
    """
    Fetches OHLCV data for a list of tickers in a single yfinance query.
    Results are cached in memory for the program's runtime.
    Returns a dict {ticker: DataFrame}.
    """
    cache_key = (tuple(sorted(tickers)), period)
    if cache_key in _data_cache:
        return _data_cache[cache_key]

    print(f"Fetching data ({period}) for {len(tickers)} tickers...")
    raw = yf.download(
        tickers,
        period=period,
        interval="1d",
        progress=False,
        auto_adjust=True,
        group_by='ticker'
    )

    result = {}
    if len(tickers) == 1:
        result[tickers[0]] = raw
    else:
        for ticker in tickers:
            try:
                df_ticker = raw[ticker].dropna(how='all')
                result[ticker] = df_ticker
            except KeyError:
                result[ticker] = pd.DataFrame()

    _data_cache[cache_key] = result
    return result

def check_balance(df):
    """
    Checks if the sum of target shares (Target_%) is 100%.
    Notifies the user if the sum is different.
    """
    total = df['Target_%'].sum()
    if round(total, 2) != 1.00:
        print("\n" + "!" * 60)
        print(f"CONFIGURATION ERROR: Target sum is {total * 100:.2f}% instead of 100%!")
        print("Adjust target weights in Edit mode so the report is correct.")
        print("!" * 60)
        return False
    return True

def fetch_eur_usd_rate():
    """
    Fetches the current EUR/USD rate from Yahoo Finance.
    On error, asks the user to provide the rate manually.
    If the user does not enter a rate, proposes the last saved rate.
    """
    try:
        data = yf.Ticker("EURUSD=X").history(period="1d")
        rate = float(data['Close'].iloc[-1])
        rate = round(rate, 2)
        rate_date = data.index[-1].date()
        with open(LAST_RATE_FILE, "w") as f:
            f.write(str(rate))
        return rate, rate_date
    except:
        last_rate = None
        if os.path.exists(LAST_RATE_FILE):
            with open(LAST_RATE_FILE) as f:
                try:
                    last_rate = round(float(f.read().strip()), 2)
                except:
                    last_rate = None
        while True:
            prompt = "Rate fetch failed. Enter EUR/USD rate"
            if last_rate:
                prompt += f" [{last_rate}]: "
            else:
                prompt += " (e.g. 1.05): "
            inp = input(prompt).replace(',', '.')
            if inp.strip() == "" and last_rate is not None:
                rate = last_rate
                break
            if inp.strip() == "":
                print("Rate is required.")
                continue
            try:
                rate = round(float(inp), 2)
                break
            except ValueError:
                print("Invalid format. Try again.")
        return rate, datetime.now().date()

def color_value(val):
    """
    Returns the value as a string with the appropriate color:
    green for positive, red for negative, default for zero.
    """
    if val > 0:
        return f"{GREEN}{val:.2f}{RESET}"
    elif val < 0:
        return f"{RED}{val:.2f}{RESET}"
    else:
        return f"{val:.2f}"

def analyze_portfolio():
    """
    Main portfolio analysis function:
    - Loads ETF data from CSV,
    - Converts values to USD,
    - Calculates current and target shares,
    - Calculates amounts and units to buy,
    - Presents a report as a table.
    """
    df = pd.read_csv(DB_FILE)
    if df.empty:
        print("No ETFs found in the database.")
        return

    df['Last_Price'] = df['Last_Price'].astype(float)
    df['Units'] = df['Units'].astype(float)
    df['Target_%'] = df['Target_%'].astype(float)

    if not check_balance(df):
        decision = input("Continue analysis despite incorrect balance? (y/n): ")
        if decision.lower() not in ('y', 't'):
            return

    eur_usd, rate_date = fetch_eur_usd_rate()
    eur_usd = float(eur_usd)
    deposit_inp = input("\nHow much USD are you adding? ").replace(',', '.')
    deposit = float(deposit_inp) if deposit_inp else 0.0

    df['Price_USD'] = df.apply(
        lambda r: r['Last_Price'] * eur_usd if r['Currency'] == 'EUR' else r['Last_Price'],
        axis=1
    )
    df['Value_USD'] = df['Units'] * df['Price_USD']

    total_usd = df['Value_USD'].sum() + deposit

    df['Actual_%'] = (df['Value_USD'] / total_usd) * 100
    df['Target_%_View'] = df['Target_%'] * 100
    df['To_Invest_USD'] = (total_usd * df['Target_%']) - df['Value_USD']
    df['To_Invest_Orig'] = df.apply(
        lambda r: r['To_Invest_USD'] / eur_usd if r['Currency'] == 'EUR' else r['To_Invest_USD'],
        axis=1
    )
    df['Units_To_Buy'] = df['To_Invest_Orig'] / df['Last_Price']

    df['To_Invest_Display'] = df['To_Invest_Orig'].apply(color_value)
    df['Units_Display'] = df['Units_To_Buy'].apply(color_value)

    print("\n" + "=" * 100)
    print(f"PORTFOLIO REPORT | Total: {total_usd:.2f} USD | EUR/USD: {eur_usd:.4f} | Rate date: {rate_date}")
    print("=" * 100)

    view_cols = ['Name', 'Currency', 'Last_Price', 'Target_%_View', 'Actual_%', 'To_Invest_Display', 'Units_Display']
    trans = df[view_cols].copy()
    trans[['Target_%_View', 'Actual_%']] = trans[['Target_%_View', 'Actual_%']].round(2)
    trans = trans.rename(columns={
        'Name': 'Asset',
        'Currency': 'Currency',
        'Last_Price': 'Price',
        'Target_%_View': 'Target (%)',
        'Actual_%': 'Actual (%)',
        'To_Invest_Display': 'Invest Amount',
        'Units_Display': 'Units to Buy'
    })

    print(tabulate(trans, headers='keys', tablefmt='pretty', showindex=False))
    print("-" * 100)

    buy_only = df[df['Units_To_Buy'] > 0]
    usd_sum = buy_only[buy_only['Currency'] == 'USD']['To_Invest_Orig'].sum()
    eur_sum = buy_only[buy_only['Currency'] == 'EUR']['To_Invest_Orig'].sum()

    print(f"TOTAL BUY AMOUNT: {usd_sum:.2f} USD | {eur_sum:.2f} EUR")
    print("=" * 100)

def show_rsi_for_portfolio():
    """
    Shows RSI (14) for ETFs in the portfolio.
    """
    df = pd.read_csv(DB_FILE)
    tickers = df['Ticker'].tolist()
    data = fetch_etf_data(tickers, period="6mo")

    print("\n" + "=" * 100)
    print("RSI (14) for portfolio ETFs:")
    print("-" * 100)
    for idx, row in df.iterrows():
        ticker = row['Ticker']
        name = row['Name']
        try:
            ticker_data = data.get(ticker, pd.DataFrame())
            if ticker_data.empty:
                print(f"{ticker:10} | {name:30} | No data.")
                continue
            stock_df = StockDataFrame.retype(ticker_data.copy())
            rsi_value = stock_df['rsi_14'].iloc[-1]
            if rsi_value <= RSI_STRONG_OVERSOLD:
                status = f"{GREEN}OPPORTUNITY (Strong oversold){RESET}"
            elif RSI_STRONG_OVERSOLD < rsi_value <= RSI_MILD_CORRECTION:
                status = f"{GREEN}ATTRACTIVE PRICE (Mild correction){RESET}"
            elif RSI_MILD_CORRECTION < rsi_value < RSI_NEUTRAL_MAX:
                status = f"{YELLOW}NEUTRAL{RESET}"
            elif RSI_NEUTRAL_MAX <= rsi_value < RSI_EXPENSIVE:
                status = f"{YELLOW}EXPENSIVE (Correction risk){RESET}"
            else:
                status = f"{RED}OVERHEATED (Do not buy){RESET}"
            print(f"{ticker:10} | {name:30} | RSI: {rsi_value:5.2f} | {status}")
        except Exception as e:
            print(f"{ticker:10} | {name:30} | Data/calculation error ({e})")

def show_correlation_matrix():
    """
    Displays the correlation matrix of daily returns for ETFs in the portfolio.
    """
    print("\n" + "=" * 100)
    print("ETF CORRELATION MATRIX (daily close change, 6 months):")
    print("-" * 100)
    df = pd.read_csv(DB_FILE)
    tickers = df['Ticker'].tolist()
    if len(tickers) < 2:
        print("Not enough ETFs for correlation analysis.")
        return

    data = fetch_etf_data(tickers, period="6mo")

    close_dfs = []
    for ticker in tickers:
        try:
            ticker_data = data.get(ticker, pd.DataFrame())
            if ticker_data.empty or 'Close' not in ticker_data.columns:
                print(f"No data for {ticker}")
                continue
            close = ticker_data[['Close']].rename(columns={'Close': ticker})
            close_dfs.append(close)
        except Exception as e:
            print(f"Data fetch error for {ticker}: {e}")

    if len(close_dfs) < 2:
        print("Not enough data for correlation analysis.")
        return

    price_df = pd.concat(close_dfs, axis=1, join='outer')
    price_df = price_df.dropna(how='all')
    price_df = price_df.dropna(axis=1, thresh=30)

    if price_df.shape[1] < 2:
        print("Not enough data for correlation analysis.")
        return

    returns = price_df.pct_change(fill_method=None).dropna()
    corr = returns.corr()

    corr.index = [str(c).split("'")[1] if isinstance(c, tuple) else str(c) for c in corr.index]
    corr.columns = [str(c).split("'")[1] if isinstance(c, tuple) else str(c) for c in corr.columns]

    def color_corr(val):
        if np.isnan(val):
            return "---"
        if val >= 0.85:
            return f"{RED}{val:.2f}{RESET}"
        elif val <= 0.5:
            return f"{GREEN}{val:.2f}{RESET}"
        else:
            return f"{YELLOW}{val:.2f}{RESET}"

    for i in range(len(corr)):
        for j in range(i):
            corr.iloc[i, j] = np.nan

    corr_display = corr.map(color_corr)
    print(tabulate(corr_display, headers='keys', tablefmt='pretty', showindex=True, numalign="center", stralign="center"))
    print("=" * 100)

def show_sma_for_portfolio():
    """
    Shows SMA 50 and SMA 200 for ETFs in the portfolio.
    """
    df = pd.read_csv(DB_FILE)
    tickers = df['Ticker'].tolist()
    data = fetch_etf_data(tickers, period="1y")

    print("\n" + "=" * 100)
    print("SMA 50 and SMA 200 for portfolio ETFs:")
    print("-" * 100)
    print(f"{'Ticker':10} | {'Name':30} | {'Price':8} | {'SMA50':8} | {'SMA200':8} | Trend")
    print("-" * 100)
    for idx, row in df.iterrows():
        ticker = row['Ticker']
        name = row['Name']
        try:
            ticker_data = data.get(ticker, pd.DataFrame())
            if ticker_data.empty or 'Close' not in ticker_data.columns:
                print(f"{ticker:10} | {name:30} | No data.")
                continue
            close = ticker_data['Close'].dropna()
            if len(close) < 200:
                print(f"{ticker:10} | {name:30} | Not enough data for SMA.")
                continue
            sma50 = close.rolling(window=50).mean().to_numpy()[-1].item()
            sma200 = close.rolling(window=200).mean().to_numpy()[-1].item()
            price = close.to_numpy()[-1].item()

            if pd.isna(sma50) or pd.isna(sma200):
                trend = "Insufficient data"
            elif sma50 > sma200:
                trend = f"{GREEN}BULLISH{RESET}"
            else:
                trend = f"{RED}BEARISH{RESET}"
            print(f"{ticker:10} | {name:30} | {price:8.2f} | {sma50:8.2f} | {sma200:8.2f} | {trend}")
        except Exception as e:
            print(f"{ticker:10} | {name:30} | Error ({e})")
    print("=" * 100)

