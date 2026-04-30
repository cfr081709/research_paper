# === Imports === #
import yfinance as yf
import pandas as pd
import numpy as np
import csv

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
# use wide range for full backtest (2000 through start of 2026)
startDate = '2000-01-01'
endDate = '2026-01-01'
fileName = "backtestingData.csv"

# Flatten stock list
tickers = stockList["nasdaqStocks"] + stockList["nyseStockExchange"]
dataOfStock = yf.download(tickers, start=startDate, end=endDate, group_by='ticker')

# === Fetch Data === #
class dataRetrieval:
    #Price Data
    def getPriceData(self, data):
        cols = ['Open', 'High', 'Low', 'Close']
        # include Volume if it exists
        if 'Volume' in data.columns:
            cols.append('Volume')
        data = data[cols]
        return data

    #Moving Average Data
    def getMovingAverageData(self, data):
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_100'] = data['Close'].rolling(window=100).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()

        data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
        data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['EMA_200'] = data['Close'].ewm(span=200, adjust=False).mean()

        return data, data['EMA_12'], data['EMA_26']
    #MACD Data
    def getMACDData(self, data, EMA_12, EMA_26):
        data['MACD'] = np.subtract(EMA_12, EMA_26)
        data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
        return data
    #ADX Data
    def getADXData(self, data):
        high = data['High']
        low = data['Low']
        close = data['Close']

        plusDM = high.diff()
        minusDM = low.diff() * -1
        plusDM[plusDM < 0] = 0
        minusDM[minusDM < 0] = 0

        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        trueRange = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = trueRange.rolling(window=14).mean()
        posDI = 100 * (plusDM.rolling(window=14).sum() / atr)
        negDI = 100 * (minusDM.rolling(window=14).sum() / atr)

        dx = (np.abs(posDI - negDI) / (posDI + negDI)) * 100
        adx = dx.rolling(window=14).mean()

        data['ADX'] = adx
        return data
    #RSI Data
    def getRSIData(self, data):
        delta = data['Close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        avgGain = pd.Series(gain).rolling(window=14).mean()
        avgLoss = pd.Series(loss).rolling(window=14).mean()

        rs = np.divide(avgGain, avgLoss, out=np.zeros_like(avgGain), where=avgLoss!=0)
        rsi = 100 - (100 / (1 + rs))

        data['RSI'] = rsi
        return data
    #OBV Data
    def getOBVData(self, data):
        # only compute OBV if Volume exists and is not all NaN
        if 'Volume' not in data.columns or data['Volume'].isna().all():
            data['OBV'] = 0
        else:
            obv = np.where(data['Close'] > data['Close'].shift(1),
                           data['Volume'],
                           np.where(data['Close'] < data['Close'].shift(1),
                                    -data['Volume'], 0))
            data['OBV'] = np.cumsum(obv)
        return data


# === Run on All Tickers === #
retriever = dataRetrieval()
allResults = []

for ticker in tickers:
    try:
        stockData = dataOfStock[ticker].copy()
        
        # ensure Volume exists; if not, create as NaN column
        if 'Volume' not in stockData.columns:
            stockData['Volume'] = np.nan

        stockData, EMA_12, EMA_26 = retriever.getMovingAverageData(stockData)
        stockData = retriever.getMACDData(stockData, EMA_12, EMA_26)
        stockData = retriever.getPriceData(stockData)
        stockData = retriever.getADXData(stockData)
        stockData = retriever.getRSIData(stockData)
        stockData = retriever.getOBVData(stockData)

        stockData['Ticker'] = ticker
        allResults.append(stockData)

    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# Combine and save
finalData = pd.concat(allResults)

# compute some basic performance metrics per ticker
metrics = []
def compute_return_metrics(price_series):
    # assume price_series is ordered by date
    returns = price_series.pct_change().dropna()
    if returns.empty:
        return np.nan, np.nan
    sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else np.nan
    cum = (1 + returns).cumprod()
    drawdown = cum / cum.cummax() - 1
    max_dd = drawdown.min()
    return sharpe, max_dd

for ticker, grp in finalData.groupby('Ticker'):
    grp = grp.sort_values('Date')
    sharpe, maxdd = compute_return_metrics(grp['Close'])
    metrics.append({'Ticker': ticker, 'Sharpe': sharpe, 'MaxDrawdown': maxdd, 'N': len(grp)})
metrics_df = pd.DataFrame(metrics)

# save data and metrics to CSV and Excel
finalData.to_csv(fileName, mode='a', header=not pd.io.common.file_exists(fileName), index=False)

xlsx_name = fileName.replace('.csv', '.xlsx')
with pd.ExcelWriter(xlsx_name) as writer:
    finalData.to_excel(writer, sheet_name='data', index=False)
    metrics_df.to_excel(writer, sheet_name='metrics', index=False)

# also export metrics separately for convenience
metrics_df.to_csv(fileName.replace('.csv', '_metrics.csv'), index=False)

print("Data Retrieval Complete - Saved to", fileName)
print("Metrics saved to", xlsx_name, "and", fileName.replace('.csv', '_metrics.csv'))
