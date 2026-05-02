import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from LSTM import build_lstm_model, create_sequences, compute_metrics
from ML import run_ml_backtest
from signal_backtester import SignalBacktester
from config import set_seed

SEED       = 42
EPOCHS     = 20
BATCH_SIZE = 32
LOOKBACK   = 10

# Resolve paths relative to this file — works regardless of working directory.
# All other files (LSTM.py, ML.py, config.py) already use this pattern.
BASE_DIR  = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "backtestingData.csv"

FEATURE_COLS = [
    "Open", "High", "Low", "Close", "Volume",
    "EMA_20", "EMA_50", "RSI_14", "MACD"
]


def load_data(path=None):
    if path is None:
        path = DATA_PATH
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"\n[ERROR] Data file not found: {path}\n"
            "You need to generate it first. Run:\n"
            "    python src/data_retrieval.py\n"
            "That script downloads price data and saves backtestingData.csv."
        )
    return pd.read_csv(path, parse_dates=["Date"])


def train_lstm():
    set_seed(SEED)

    df = load_data()
    all_metrics = []

    for ticker in sorted(df["Ticker"].unique()):
        grp = df[df["Ticker"] == ticker].copy()
        grp = grp.sort_values("Date").reset_index(drop=True)

        # Ensure Return target column exists
        if "Return" not in grp.columns:
            grp["Return"] = grp["Close"].pct_change().shift(-1)

        available = [c for c in FEATURE_COLS if c in grp.columns]
        if len(available) < 4:
            print(f"[SKIP] {ticker}: insufficient feature columns ({available})")
            continue

        grp = grp.dropna(subset=available + ["Return"]).reset_index(drop=True)

        if len(grp) < LOOKBACK + 50:
            print(f"[SKIP] {ticker}: insufficient rows ({len(grp)})")
            continue

        X      = grp[available].values
        y      = grp["Return"].values
        dates  = grp["Date"]
        split  = int(len(grp) * 0.8)

        # Fit scaler on train only — no data leakage
        scaler   = MinMaxScaler()
        X_scaled = np.vstack([
            scaler.fit_transform(X[:split]),
            scaler.transform(X[split:])
        ])

        X_train, y_train, _ = create_sequences(X_scaled, y, dates, LOOKBACK, split,    LOOKBACK)
        X_test,  y_test,  _ = create_sequences(X_scaled, y, dates, split,    len(grp), LOOKBACK)

        if len(X_train) == 0 or len(X_test) == 0:
            continue

        model = build_lstm_model(n_features=len(available), time_step=LOOKBACK)

        model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            verbose=0,
            shuffle=False       # preserve time-series order
        )

        loss, mae = model.evaluate(X_test, y_test, verbose=0)
        preds = model.predict(X_test, verbose=0).reshape(-1)
        actual = y_test

        mae_comp, rmse, sharpe, max_dd, cagr, _, _ = compute_metrics(actual, preds)
        print(f"[{ticker}]  MAE: {mae_comp:.6f}  RMSE: {rmse:.6f}  Sharpe: {sharpe:.6f}  Max_DD: {max_dd:.6f}  CAGR: {cagr:.6f}")
        all_metrics.append({
            "Ticker": ticker,
            "MAE": mae_comp,
            "RMSE": rmse,
            "Sharpe": sharpe,
            "Max_Drawdown": max_dd,
            "CAGR": cagr
        })

    results_dir = BASE_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "metrics").mkdir(parents=True, exist_ok=True)

    metrics_df = pd.DataFrame(all_metrics)
    metrics_df.to_csv(results_dir / "full_backtest_summary.csv", index=False)
    metrics_df.to_csv(results_dir / "metrics" / "lstm_metrics.csv", index=False)
    print("\nFull backtest complete.")
    print(metrics_df)
    return metrics_df


if __name__ == "__main__":
    results_dir = BASE_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "metrics").mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Running LSTM backtest...")
    print("=" * 60)
    lstm_metrics = train_lstm()

    print("\n" + "=" * 60)
    print("Running ML backtest...")
    print("=" * 60)
    ml_metrics = run_ml_backtest(pd.read_csv(DATA_PATH, parse_dates=["Date"]))

    print("\n" + "=" * 60)
    print("Running Signal backtest...")
    print("=" * 60)
    signal_bt = SignalBacktester(price_csv=DATA_PATH)
    signal_metrics = signal_bt.run()

    print("\n" + "=" * 60)
    print("Combined Results Summary")
    print("=" * 60)
    print("\nLSTM Metrics:")
    print(lstm_metrics)
    print("\nML Metrics:")
    print(ml_metrics)
    print("\nSignal Metrics:")
    print(signal_metrics)
