import pandas as pd
import numpy as np
from pathlib import Path

class SignalBacktester:

    DEFAULT_BULLISH = {
        'SMA_Trend': ['Strong Uptrend'],
        'EMA_Trend': ['Strong Uptrend'],
        'MACD_Trend': ['Bullish Momentum'],
        'ADX_Trend': ['Strong Trend', 'Very Strong Trend', 'Extremely Strong Trend'],
        'OBV_Trend': ['Buying Pressure'],
    }

    DEFAULT_BEARISH = {
        'SMA_Trend': ['Strong Downtrend'],
        'EMA_Trend': ['Strong Downtrend'],
        'MACD_Trend': ['Bearish Momentum'],
        'OBV_Trend': ['Selling Pressure'],
    }

    def __init__(self, price_csv, analysis_csv, start_date=None, end_date=None):
        self.price_csv = Path(price_csv)
        self.analysis_csv = Path(analysis_csv)
        self.start_date = pd.to_datetime(start_date) if start_date else None
        self.end_date = pd.to_datetime(end_date) if end_date else None
        self._load()

    def _load(self):
        self.prices = pd.read_csv(self.price_csv, parse_dates=['Date'])
        self.analysis = pd.read_csv(self.analysis_csv, parse_dates=['Date'])

        if self.start_date is not None:
            self.prices = self.prices[self.prices['Date'] >= self.start_date]
            self.analysis = self.analysis[self.analysis['Date'] >= self.start_date]

        if self.end_date is not None:
            self.prices = self.prices[self.prices['Date'] <= self.end_date]
            self.analysis = self.analysis[self.analysis['Date'] <= self.end_date]

        self.data = pd.merge(
            self.analysis,
            self.prices,
            on=['Ticker', 'Date'],
            how='left'
        )

    def run(self, lookahead=1):

        self.data = self.data.sort_values(['Ticker', 'Date']).reset_index(drop=True)

        # ✅ Forward return (correct)
        self.data['Return'] = (
            self.data.groupby('Ticker')['Close']
            .pct_change(periods=lookahead)
            .shift(-lookahead)
        )

        # 🔥 NEW: Regime-aware signal
        self.data['Signal'] = 0.0

        # --- TREND COMPONENT ---
        trend_score = 0
        trend_cols = ['SMA_Trend', 'EMA_Trend', 'MACD_Trend']

        for col in trend_cols:
            trend_score += self.data[col].isin(self.DEFAULT_BULLISH.get(col, [])).astype(int)
            trend_score -= self.data[col].isin(self.DEFAULT_BEARISH.get(col, [])).astype(int)

        # --- ADX FILTER ---
        strong_trend = self.data['ADX_Trend'].isin(
            ['Strong Trend', 'Very Strong Trend', 'Extremely Strong Trend']
        )

        # --- RSI (ONLY WHEN NOT TRENDING) ---
        rsi_signal = np.where(
            ~strong_trend,
            np.where(self.data['RSI_Trend'] == 'Oversold', 1,
            np.where(self.data['RSI_Trend'] == 'Overbought', -1, 0)),
            0
        )

        # --- FINAL SIGNAL ---
        self.data['Signal'] = (trend_score / len(trend_cols)) + rsi_signal

        # Normalize
        self.data['Signal'] = self.data['Signal'].clip(-1, 1)

        # Strategy return
        self.data['Strategy_Return'] = self.data['Signal'] * self.data['Return']

        valid = self.data.dropna(subset=['Strategy_Return'])

        # ✅ PER-TICKER ANALYSIS (PROFESSOR REQUEST)
        ticker_stats = valid.groupby('Ticker')['Strategy_Return'].agg(['mean', 'std'])

        overall_returns = valid['Strategy_Return'].values

        sharpe = self._sharpe(overall_returns)
        maxdd = self._max_drawdown(overall_returns)

        metrics_df = pd.DataFrame([{
            'n_trades': len(overall_returns),
            'avg_return': np.mean(overall_returns),
            'Sharpe': sharpe,
            'MaxDrawdown': maxdd,
            'std_across_tickers': ticker_stats['mean'].std(),  # 🔥 KEY ADD
            'worst_ticker_return': ticker_stats['mean'].min()
        }])

        metrics_df.to_csv('Final Backtest Data/signal_backtest_metrics.csv', index=False)
        ticker_stats.to_csv('Final Backtest Data/per_ticker_stats.csv')

        return metrics_df

    def _sharpe(self, returns):
        r = pd.Series(returns).dropna()
        if r.std() < 1e-6:
            return 0
        return r.mean() / r.std() * np.sqrt(252)

    def _max_drawdown(self, returns):
        r = pd.Series(returns).dropna()
        cum = (1 + r).cumprod()
        dd = cum / cum.cummax() - 1
        return dd.min()


if __name__ == '__main__':
    sb = SignalBacktester(
        price_csv='backtestingData.csv',
        analysis_csv='dataAnalysis.csv'
    )
    print(sb.run())