# === Imports === #
import yfinance as yf
import pandas as pd
import numpy as np
import os

# === Stock Data Set === #
stockList = {
    "nasdaqStocks": [
        'TSLA','INTC','SBUX','DELL','AMZN','AAPL','HIMS','META','GOOGL','NVDA',
        'BRK-B','ORCL','WMT','V','MA','NFLX','COST','JNJ','PFE'
    ],
    "nyseStockExchange": [
        'JPM','GS','GIS','FDX','T','BAC','XOM','CVX','BA','MCD'
    ]
}

# === Const. Variables === #
startDate = '2000-01-01'
endDate = '2026-01-01'
fileName = "data/backtestingData.csv"

tickers = stockList["nasdaqStocks"] + stockList["nyseStockExchange"]

# === Download Data === #
data = yf.download(
    tickers,
    start=startDate,
    end=endDate,
    auto_adjust=True,
    progress=False
)

# Ensure reproducibility
data = data.sort_index()

# === Feature Engineering Class === #
class DataEngineer:

    def process_ticker(self, df, ticker):
        df = df.copy()

        # Reset index
        df = df.reset_index()
        df.rename(columns={"Date": "Date"}, inplace=True)

        # === Basic Features === #
        df['Return'] = df['Close'].pct_change()
        df['LogReturn'] = np.log(df['Close'] / df['Close'].shift(1))

        # === Volatility === #
        df['Volatility_20'] = df['Return'].rolling(20).std()

        # === Moving Averages === #
        for w in [20, 50, 100, 200]:
            df[f'SMA_{w}'] = df['Close'].rolling(w).mean()

        for w in [12, 26, 50, 200]:
            df[f'EMA_{w}'] = df['Close'].ewm(span=w, adjust=False).mean()

        # === MACD === #
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # === RSI (FIXED) === #
        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # === ADX (Improved) === #
        high = df['High']
        low = df['Low']
        close = df['Close']

        # Wilder's DM: each bar only contributes to plus OR minus, not both
        raw_plus  = high.diff()
        raw_minus = -low.diff()
        plus_dm  = np.where((raw_plus > raw_minus) & (raw_plus > 0), raw_plus,  0.0)
        minus_dm = np.where((raw_minus > raw_plus) & (raw_minus > 0), raw_minus, 0.0)
        plus_dm  = pd.Series(plus_dm,  index=high.index)
        minus_dm = pd.Series(minus_dm, index=high.index)

        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)

        atr = tr.rolling(14).mean()

        plus_di = 100 * (plus_dm.rolling(14).sum() / atr)
        minus_di = 100 * (minus_dm.rolling(14).sum() / atr)

        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        df['ADX'] = dx.rolling(14).mean()

        # === OBV === #
        if 'Volume' in df.columns:
            direction = np.sign(df['Close'].diff()).fillna(0)
            df['OBV'] = (direction * df['Volume']).cumsum()
        else:
            df['OBV'] = 0

        # === Lag Features (VERY IMPORTANT FOR ML) === #
        for lag in [1, 2, 3, 5, 10]:
            df[f'Return_lag_{lag}'] = df['Return'].shift(lag)

        # === Target Variable (for ML) === #
        df['Target'] = df['Return'].shift(-1)

        df['Ticker'] = ticker

        return df


# === Process All Tickers === #
engineer = DataEngineer()
all_data = []

for ticker in tickers:
    try:
        df = data.xs(ticker, axis=1, level=1)
        processed = engineer.process_ticker(df, ticker)
        all_data.append(processed)
    except Exception as e:
        print(f"[ERROR] {ticker}: {e}")

finalData = pd.concat(all_data, ignore_index=True)

# === Clean Data === #
finalData = finalData.sort_values(['Ticker', 'Date'])

# Drop early NaNs from indicators
finalData = finalData.dropna().reset_index(drop=True)

# === Metrics === #
def compute_metrics(df):
    returns = df['Return']
    sharpe = np.sqrt(252) * returns.mean() / returns.std() if returns.std() != 0 else np.nan

    cum = (1 + returns).cumprod()
    drawdown = cum / cum.cummax() - 1

    return pd.Series({
        "Sharpe": sharpe,
        "MaxDrawdown": drawdown.min(),
        "N": len(df)
    })

metrics_df = finalData.groupby('Ticker').apply(compute_metrics, include_groups=False).reset_index()

# === Save (REPRODUCIBLE) === #
os.makedirs("data", exist_ok=True)

finalData.to_csv(fileName, index=False)
metrics_df.to_csv(fileName.replace(".csv", "_metrics.csv"), index=False)

print("✅ Data Retrieval + Feature Engineering Complete")
