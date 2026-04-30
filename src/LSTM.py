import os
import random
import json
import hashlib
from pathlib import Path
from datetime import datetime
from config import *

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

import tensorflow as tf

SEED = 42
BASE_DIR = Path(__file__).resolve().parent.parent

os.environ["PYTHONHASHSEED"] = str(SEED)
os.environ["TF_DETERMINISTIC_OPS"] = "1"
os.environ["TF_CUDNN_DETERMINISTIC"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # CPU-only for strict reproducibility

random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

class LSTMModel:

    def __init__(self, df):
        self.data = df.copy()

    def add_indicators(self, df):
        df = df.copy()

        df['EMA_20'] = df['Close'].ewm(span=20).mean()
        df['EMA_50'] = df['Close'].ewm(span=50).mean()

        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        rs = gain.rolling(14).mean() / (loss.rolling(14).mean() + 1e-8)
        df['RSI_14'] = 100 - (100 / (1 + rs))

        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        df['MACD'] = ema12 - ema26

        df['Return'] = df['Close'].pct_change().shift(-1)

        return df.dropna().reset_index(drop=True)

    @staticmethod
    def create_sequences(X, y, time_step):
        Xs, ys = [], []
        for i in range(len(X) - time_step):
            Xs.append(X[i:i + time_step])
            ys.append(y[i + time_step])
        return np.array(Xs), np.array(ys)

    def train_and_backtest(self, test_ratio=0.2, time_step=60, epochs=5):

        all_preds = []
        metrics = []

        feature_cols = [
            'Open', 'High', 'Low', 'Close', 'Volume',
            'EMA_20', 'EMA_50', 'RSI_14', 'MACD'
        ]

        Path("Final Backtest Data").mkdir(parents=True, exist_ok=True)

        for ticker in sorted(self.data['Ticker'].unique()):

            grp = self.data[self.data['Ticker'] == ticker].copy()
            grp = grp.sort_values('Date').reset_index(drop=True)

            grp = self.add_indicators(grp)

            if len(grp) < time_step + 50:
                continue

            X = grp[feature_cols].values
            y = grp['Return'].values

            split = int(len(X) * (1 - test_ratio))

            X_train_raw, X_test_raw = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]

            from sklearn.preprocessing import MinMaxScaler

            scaler = MinMaxScaler()
            X_train = scaler.fit_transform(X_train_raw)
            X_test = scaler.transform(X_test_raw)

            X_train, y_train = self.create_sequences(X_train, y_train, time_step)
            X_test, y_test = self.create_sequences(X_test, y_test, time_step)

            if len(X_train) == 0 or len(X_test) == 0:
                continue

            tf.keras.backend.clear_session()

            initializer = tf.keras.initializers.GlorotUniform(seed=SEED)

            model = tf.keras.Sequential([
                tf.keras.layers.LSTM(
                    64,
                    return_sequences=True,
                    kernel_initializer=initializer,
                    recurrent_initializer=initializer,
                    input_shape=(time_step, len(feature_cols))
                ),
                tf.keras.layers.Dropout(0.2, seed=SEED),

                tf.keras.layers.LSTM(
                    32,
                    kernel_initializer=initializer,
                    recurrent_initializer=initializer
                ),

                tf.keras.layers.Dense(1, kernel_initializer=initializer)
            ])

            model.compile(optimizer='adam', loss='mse')

            model.fit(
                X_train,
                y_train,
                epochs=epochs,
                batch_size=32,
                verbose=0,
                shuffle=False
            )

            preds = model.predict(X_test, verbose=0).flatten()
            actual = y_test

            signal = np.where(preds > 0, 1, -1)
            strategy_returns = signal * actual

            # Stable Sharpe
            std = np.std(strategy_returns)
            sharpe = (np.mean(strategy_returns) / (std + 1e-8) * np.sqrt(252)) if std > 0 else 0

            cumulative = (1 + strategy_returns).cumprod()
            max_dd = (cumulative / np.maximum.accumulate(cumulative) - 1).min()
            cagr = cumulative[-1] ** (252 / len(strategy_returns)) - 1

            mae = np.mean(np.abs(actual - preds))
            rmse = np.sqrt(np.mean((actual - preds) ** 2))

            metrics.append({
                'Ticker': ticker,
                'Model': 'LSTM',
                'MAE': mae,
                'RMSE': rmse,
                'Sharpe': sharpe,
                'Max_Drawdown': max_dd,
                'CAGR': cagr
            })

            dates = grp['Date'].iloc[split + time_step:].reset_index(drop=True)

            all_preds.append(pd.DataFrame({
                'Date': dates,
                'Ticker': ticker,
                'Model': 'LSTM',
                'Actual_Return': actual,
                'Pred_Return': preds,
                'Signal': signal,
                'Strategy_Return': strategy_returns
            }))

        preds_df = pd.concat(all_preds, ignore_index=True)
        metrics_df = pd.DataFrame(metrics)

        preds_df.to_csv('Final Backtest Data/lstm_predictions.csv', index=False)
        metrics_df.to_csv('Final Backtest Data/lstm_metrics.csv', index=False)

        preds_df.to_excel('Final Backtest Data/lstm_predictions.xlsx', index=False)
        metrics_df.to_excel('Final Backtest Data/lstm_metrics.xlsx', index=False)

        metadata = {
            "seed": SEED,
            "test_ratio": test_ratio,
            "time_step": time_step,
            "epochs": epochs,
            "model": "LSTM",
            "features": feature_cols,
            "data_hash": file_hash(BASE_DIR / "data" / "backtestingData.csv"),
            "timestamp": datetime.now().isoformat()
        }

        with open(BASE_DIR / "results" / "metadata" / "LSTM.json", "w") as f:
            json.dump(metadata, f, indent=4)

        plt.figure(figsize=(10, 6))
        plt.scatter(preds_df['Actual_Return'], preds_df['Pred_Return'], alpha=0.5)
        plt.xlabel('Actual Return')
        plt.ylabel('Predicted Return')
        plt.title('LSTM Predicted vs Actual Returns')
        plt.grid(True)
        plt.savefig('Final Backtest Data/lstm_pred_vs_actual.png')
        plt.close()

        return metrics_df

if __name__ == '__main__':
    df = pd.read_csv(BASE_DIR / "data" / "backtestingData.csv", parse_dates=['Date'])

    model = LSTMModel(df)
    metrics = model.train_and_backtest()

    print("\nLSTM backtest metrics:")
    print(metrics)