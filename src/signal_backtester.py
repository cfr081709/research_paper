import pandas as pd
import numpy as np
from pathlib import Path
import os


class SignalBacktester:

    def __init__(self, price_csv, start_date=None, end_date=None):
        self.price_csv = Path(price_csv)
        self.start_date = pd.to_datetime(start_date) if start_date else None
        self.end_date = pd.to_datetime(end_date) if end_date else None
        self.load()

    # =========================
    # LOAD + CLEAN DATA
    # =========================
    def load(self):
        df = pd.read_csv(self.price_csv)

        # 🔥 Robust Date handling (fixes your earlier error permanently)
        df.columns = [c.strip() for c in df.columns]

        if 'Date' not in df.columns:
            # try fallback
            for c in df.columns:
                if c.lower() in ['date', 'datetime', 'timestamp']:
                    df.rename(columns={c: 'Date'}, inplace=True)

        if 'Date' not in df.columns:
            raise ValueError(f"No Date column found. Columns: {df.columns}")

        df['Date'] = pd.to_datetime(df['Date'])

        # Filter dates
        if self.start_date is not None:
            df = df[df['Date'] >= self.start_date]
        if self.end_date is not None:
            df = df[df['Date'] <= self.end_date]

        # Sort
        df = df.sort_values(['Ticker', 'Date']).reset_index(drop=True)

        self.data = df

    # =========================
    # SIGNAL ENGINE
    # =========================
    def _build_signals(self):

        df = self.data

        # --- TREND SIGNAL (MA CROSS) ---
        trend = np.where(df['SMA_50'] > df['SMA_200'], 1,
                 np.where(df['SMA_50'] < df['SMA_200'], -1, 0))

        # --- MOMENTUM (MACD) ---
        macd = np.where(df['MACD'] > df['MACD_Signal'], 1,
                np.where(df['MACD'] < df['MACD_Signal'], -1, 0))

        # --- ADX FILTER (strength only) ---
        strong_trend = df['ADX'] > 25

        # --- RSI MEAN REVERSION (only when weak trend) ---
        rsi = np.where(~strong_trend,
                np.where(df['RSI'] < 30, 1,
                np.where(df['RSI'] > 70, -1, 0)),
                0)

        # --- COMBINE SIGNALS ---
        signal = (0.5 * trend + 0.3 * macd + 0.2 * rsi)

        # Normalize
        signal = np.clip(signal, -1, 1)

        df['Signal'] = signal

        return df

    # =========================
    # BACKTEST
    # =========================
    def run(self, lookahead=1):

        df = self.data.copy()

        # 🔥 Forward returns (correct, no lookahead bias)
        df['Return'] = (
            df.groupby('Ticker')['Close']
            .pct_change(periods=lookahead)
            .shift(-lookahead)
        )

        # Build signals
        df = self._build_signals()

        # Strategy returns
        df['Strategy_Return'] = df['Signal'] * df['Return']

        valid = df.dropna(subset=['Strategy_Return'])

        # =========================
        # METRICS
        # =========================

        ticker_stats = valid.groupby('Ticker')['Strategy_Return'].agg(['mean', 'std'])

        overall_returns = valid['Strategy_Return']

        sharpe = self._sharpe(overall_returns)
        maxdd = self._max_drawdown(overall_returns)

        metrics_df = pd.DataFrame([{
            'n_obs': len(valid),
            'avg_return': overall_returns.mean(),
            'Sharpe': sharpe,
            'MaxDrawdown': maxdd,
            'std_across_tickers': ticker_stats['mean'].std(),
            'worst_ticker_return': ticker_stats['mean'].min()
        }])

        # =========================
        # SAVE OUTPUTS
        # =========================
        os.makedirs("results", exist_ok=True)

        metrics_df.to_csv('results/signal_backtest_metrics.csv', index=False)
        ticker_stats.to_csv('results/per_ticker_stats.csv')
        df.to_csv('results/full_backtest_output.csv', index=False)

        return metrics_df

    # =========================
    # METRICS
    # =========================
    def _sharpe(self, returns):
        r = pd.Series(returns).dropna()
        if r.std() < 1e-8:
            return 0
        return np.sqrt(252) * r.mean() / r.std()

    def _max_drawdown(self, returns):
        r = pd.Series(returns).dropna()
        cum = (1 + r).cumprod()
        dd = cum / cum.cummax() - 1
        return dd.min()


# =========================
# RUN
# =========================
if __name__ == '__main__':
    sb = SignalBacktester(price_csv='data/backtestingData.csv')
    print(sb.run())