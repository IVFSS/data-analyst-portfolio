import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")


def download_stock_data(ticker="AAPL", period="1y"):
    print(f"Downloading {ticker} stock data...")
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    print(f"Downloaded {len(df)} rows")
    return df


def time_series_analysis(df, ticker):
    print("\n" + "=" * 50)
    print(f"TIME SERIES ANALYSIS - {ticker}")
    print("=" * 50)

    print(f"\nDate Range: {df.index.min()} to {df.index.max()}")
    print(f"\nBasic Statistics:\n{df.describe()}")

    df["Returns"] = df["Close"].pct_change()
    df["MA_7"] = df["Close"].rolling(window=7).mean()
    df["MA_30"] = df["Close"].rolling(window=30).mean()

    print(f"\nDaily Returns Statistics:")
    print(f"Mean: {df['Returns'].mean() * 100:.4f}%")
    print(f"Std Dev: {df['Returns'].std() * 100:.4f}%")
    print(f"Max: {df['Returns'].max() * 100:.4f}%")
    print(f"Min: {df['Returns'].min() * 100:.4f}%")

    return df


def create_stock_visualizations(df, ticker):
    print("\n" + "=" * 50)
    print("CREATING VISUALIZATIONS")
    print("=" * 50)

    fig, axes = plt.subplots(3, 1, figsize=(14, 12))

    axes[0].plot(df.index, df["Close"], label="Close Price", linewidth=1.5)
    axes[0].plot(df.index, df["MA_7"], label="7-Day MA", alpha=0.8, linewidth=1)
    axes[0].plot(df.index, df["MA_30"], label="30-Day MA", alpha=0.8, linewidth=1)
    axes[0].set_title(f"{ticker} Stock Price with Moving Averages")
    axes[0].set_ylabel("Price ($)")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].bar(df.index, df["Volume"], alpha=0.6, color="steelblue")
    axes[1].set_title(f"{ticker} Trading Volume")
    axes[1].set_ylabel("Volume")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(df.index, df["Returns"], alpha=0.5, linewidth=0.8)
    axes[2].axhline(y=0, color="r", linestyle="--", alpha=0.5)
    axes[2].set_title(f"{ticker} Daily Returns")
    axes[2].set_ylabel("Return")
    axes[2].set_xlabel("Date")
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, f"stock_analysis_{ticker}.png"), dpi=150)
    print(f"Saved: {OUTPUT_PATH}/stock_analysis_{ticker}.png")
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(df["Returns"].dropna(), bins=50, edgecolor="black", alpha=0.7)
    axes[0].set_title("Distribution of Daily Returns")
    axes[0].set_xlabel("Return")
    axes[0].set_ylabel("Frequency")
    axes[0].axvline(
        x=df["Returns"].mean(),
        color="r",
        linestyle="--",
        label=f"Mean: {df['Returns'].mean() * 100:.2f}%",
    )
    axes[0].legend()

    monthly = df["Close"].resample("ME").last()
    monthly_returns = monthly.pct_change().dropna()
    axes[1].bar(
        range(len(monthly_returns)),
        monthly_returns.values * 100,
        alpha=0.7,
        color="steelblue",
    )
    axes[1].set_title("Monthly Returns")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Return (%)")
    axes[1].axhline(y=0, color="r", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, f"stock_returns_{ticker}.png"), dpi=150)
    print(f"Saved: {OUTPUT_PATH}/stock_returns_{ticker}.png")
    plt.close()


def main():
    print("=" * 60)
    print("STOCK PRICE TIME SERIES ANALYSIS")
    print("=" * 60)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    ticker = "AAPL"
    df = download_stock_data(ticker, period="1y")

    df = time_series_analysis(df, ticker)
    create_stock_visualizations(df, ticker)

    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE!")
    print("=" * 50)


if __name__ == "__main__":
    main()
