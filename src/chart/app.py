import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt

def show_chart(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        print("No data available. Possible Yahoo Finance rate limit exceeded or download error.")
        return

    df = df.apply(pd.to_numeric, errors='coerce')
    close_series = df["Close"].squeeze()

    macd = ta.trend.MACD(
        close=close_series,
        window_slow=21,
        window_fast=8,
        window_sign=9
    )
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    df["MACD_histogram"] = macd.macd_diff()

    sma50 = ta.trend.SMAIndicator(close=close_series, window=50)
    df["SMA50"] = sma50.sma_indicator()

    plt.figure(figsize=(14, 8))
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df["Close"], label="Close Price", color="black")
    plt.plot(df.index, df["SMA50"], label="SMA50", color="blue", linestyle="--")
    last_close = df["Close"].iloc[-1].item()
    last_date = df.index[-1]
    adjusted_date = last_date + pd.Timedelta(days=1)
    plt.text(
        x=adjusted_date,
        y=last_close,
        s=f"{last_close:.2f}",
        color="red",
        fontsize=10,
        fontweight="bold",
        horizontalalignment='left'
    )
    plt.title(f"{ticker} Price + SMA50")
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(df.index, df["MACD"], label="MACD (8,21)", color="green")
    plt.plot(df.index, df["MACD_signal"], label="Signal (9)", color="red", linestyle="--")
    plt.bar(df.index, df["MACD_histogram"], label="Histogram", color="gray", alpha=0.5)
    plt.axhline(0, color="black", linewidth=1, linestyle="--")
    plt.title("MACD Indicator")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()
