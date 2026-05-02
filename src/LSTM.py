import os
import random
import json
import hashlib
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

from sklearn.preprocessing import MinMaxScaler


# =========================
# SETUP
# =========================
SEED = 42
os.environ["PYTHONHASHSEED"] = str(SEED)
os.environ["TF_DETERMINISTIC_OPS"] = "1"
os.environ["TF_CUDNN_DETERMINISTIC"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

random.seed(SEED)
np.random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent.parent


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load_tensorflow():
    try:
        import tensorflow as tf
        from tensorflow.keras import Sequential
        from tensorflow.keras.layers import Dense, Dropout, Input, LSTM
        from tensorflow.keras.optimizers import Adam

        tf.random.set_seed(SEED)
        return tf, Sequential, Input, LSTM, Dropout, Dense, Adam
    except ImportError as exc:
        raise ImportError(
            "TensorFlow is required for the LSTM backtest. Install dependencies "
            "with `python -m pip install -r requirements.txt`, then run "
            "`python src/LSTM.py` again."
        ) from exc

def add_features(df):
    df = df.copy()

    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    rs = gain.rolling(14).mean() / (loss.rolling(14).mean() + 1e-8)
    df["RSI_14"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26

    # Forward return target: next-period percentage return.
    df["Return"] = df["Close"].pct_change().shift(-1)

    return df.dropna().reset_index(drop=True)


def create_sequences(X, y, dates, start_idx, end_idx, time_step):
    X_seq, y_seq, date_seq = [], [], []

    for idx in range(start_idx, end_idx):
        if idx - time_step < 0:
            continue
        X_seq.append(X[idx - time_step:idx])
        y_seq.append(y[idx])
        date_seq.append(dates.iloc[idx])

    return np.array(X_seq), np.array(y_seq), pd.Series(date_seq)


def build_lstm_model(n_features, time_step, learning_rate=0.001):
    _, Sequential, Input, LSTM, Dropout, Dense, Adam = load_tensorflow()

    model = Sequential([
        Input(shape=(time_step, n_features)),
        LSTM(32, activation="tanh"),
        Dropout(0.2),
        Dense(16, activation="relu"),
        Dense(1)
    ])

    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss="mse",
        metrics=["mae"]
    )

    return model


def compute_metrics(actual, preds):
    signal = np.where(preds > 0, 1, -1)
    strategy_returns = signal * actual

    std = np.std(strategy_returns)
    sharpe = (np.mean(strategy_returns) / (std + 1e-8)) * np.sqrt(252) if std > 0 else 0

    cumulative = (1 + strategy_returns).cumprod()
    max_dd = (cumulative / np.maximum.accumulate(cumulative) - 1).min()
    cagr = cumulative[-1] ** (252 / len(strategy_returns)) - 1

    mae = np.mean(np.abs(actual - preds))
    rmse = np.sqrt(np.mean((actual - preds) ** 2))

    return mae, rmse, sharpe, max_dd, cagr, signal, strategy_returns


# =========================
# MAIN BACKTEST
# =========================
def run_lstm_backtest(
    df,
    test_ratio=0.2,
    time_step=60,
    epochs=10,
    batch_size=32,
    start_date=None,
    end_date=None
):
    load_tensorflow()

    Path("results/predictions").mkdir(parents=True, exist_ok=True)
    Path("results/metrics").mkdir(parents=True, exist_ok=True)
    Path("results/metadata").mkdir(parents=True, exist_ok=True)
    Path("results/graphs").mkdir(parents=True, exist_ok=True)

    if start_date:
        df = df[df["Date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["Date"] <= pd.to_datetime(end_date)]

    all_preds = []
    metrics = []

    feature_cols = [
        "Open", "High", "Low", "Close", "Volume",
        "EMA_20", "EMA_50", "RSI_14", "MACD"
    ]

    for ticker in sorted(df["Ticker"].unique()):
        grp = df[df["Ticker"] == ticker].copy()
        grp = grp.sort_values("Date").reset_index(drop=True)
        grp = add_features(grp)

        if len(grp) < time_step + 90:
            continue

        X = grp[feature_cols].values
        y = grp["Return"].values
        dates = grp["Date"].reset_index(drop=True)

        split = int(len(grp) * (1 - test_ratio))
        if split <= time_step or split >= len(grp):
            continue

        scaler = MinMaxScaler()
        X_train_raw = scaler.fit_transform(X[:split])
        X_all = np.vstack([X_train_raw, scaler.transform(X[split:])])

        X_train, y_train, _ = create_sequences(
            X_all, y, dates, time_step, split, time_step
        )
        X_test, y_test, test_dates = create_sequences(
            X_all, y, dates, split, len(grp), time_step
        )

        if len(X_train) == 0 or len(X_test) == 0:
            continue

        try:
            model = build_lstm_model(
                n_features=len(feature_cols),
                time_step=time_step
            )
            model.fit(
                X_train,
                y_train,
                epochs=epochs,
                batch_size=batch_size,
                verbose=0,
                shuffle=False,
                validation_split=0.1
            )

            preds = model.predict(X_test, verbose=0).reshape(-1)
            actual = y_test

            mae, rmse, sharpe, max_dd, cagr, signal, strategy_returns = compute_metrics(
                actual, preds
            )

            metrics.append({
                "Ticker": ticker,
                "Model": "LSTM",
                "MAE": mae,
                "RMSE": rmse,
                "Sharpe": sharpe,
                "Max_Drawdown": max_dd,
                "CAGR": cagr
            })

            all_preds.append(pd.DataFrame({
                "Date": test_dates.reset_index(drop=True),
                "Ticker": ticker,
                "Model": "LSTM",
                "Actual_Return": actual,
                "Pred_Return": preds,
                "Signal": signal,
                "Strategy_Return": strategy_returns
            }))

        except Exception as e:
            print(f"[ERROR] {ticker} - LSTM: {e}")

    if len(all_preds) == 0:
        raise ValueError("No LSTM predictions generated - check data length and TensorFlow setup.")

    preds_df = pd.concat(all_preds, ignore_index=True)
    metrics_df = pd.DataFrame(metrics)

    preds_df.to_csv("results/predictions/lstm_predictions.csv", index=False)
    metrics_df.to_csv("results/metrics/lstm_metrics.csv", index=False)

    metadata = {
        "seed": SEED,
        "test_ratio": test_ratio,
        "time_step": time_step,
        "epochs": epochs,
        "batch_size": batch_size,
        "model": "LSTM",
        "features": feature_cols,
        "data_hash": file_hash(BASE_DIR / "data" / "backtestingData.csv"),
        "timestamp": datetime.now().isoformat()
    }

    with open(BASE_DIR / "results" / "metadata" / "LSTM.json", "w") as f:
        json.dump(metadata, f, indent=4)

    plt.figure(figsize=(10, 6))
    plt.scatter(preds_df["Actual_Return"], preds_df["Pred_Return"], alpha=0.5)
    plt.xlabel("Actual Return")
    plt.ylabel("Predicted Return")
    plt.title("LSTM Predicted vs Actual Returns")
    plt.grid(True)
    plt.savefig("results/graphs/LSTM_pred_vs_actual.png")
    plt.close()

    return metrics_df

if __name__ == "__main__":
    df = pd.read_csv(BASE_DIR / "data" / "backtestingData.csv", parse_dates=["Date"])

    metrics = run_lstm_backtest(df)

    print("\nLSTM backtest metrics:")
    print(metrics)
