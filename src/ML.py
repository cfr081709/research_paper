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

from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# NOTE:
# Rolling indicators such as SMA200 may introduce look-ahead bias if computed
# on the full dataset before splitting. Ideally, indicators should be computed
# separately on train/test splits. This is acknowledged as a limitation.

SEED = 42

os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)

print(f"Using seed: {SEED}")

def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def run_ml_backtest(df, test_ratio=0.2, start_date=None, end_date=None):

    Path("Final Backtest Data").mkdir(parents=True, exist_ok=True)

    if start_date:
        df = df[df['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Date'] <= pd.to_datetime(end_date)]

    all_preds = []
    metrics = []

    feature_cols = [
        'Open','High','Low','Close','Volume',
        'EMA_20','EMA_50','RSI_14','MACD'
    ]

    model_names = ["Linear", "RandomForest", "GradientBoosting", "Polynomial"]

    for ticker in sorted(df['Ticker'].unique()):
        grp = df[df['Ticker'] == ticker].copy()
        grp = grp.sort_values('Date').reset_index(drop=True)

        grp['EMA_20'] = grp['Close'].ewm(span=20, adjust=False).mean()
        grp['EMA_50'] = grp['Close'].ewm(span=50, adjust=False).mean()

        delta = grp['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        rs = gain.rolling(14).mean() / (loss.rolling(14).mean() + 1e - 8)
        grp['RSI_14'] = 100 - (100 / (1 + rs))

        ema12 = grp['Close'].ewm(span=12, adjust=False).mean()
        ema26 = grp['Close'].ewm(span=26, adjust=False).mean()
        grp['MACD'] = ema12 - ema26

        grp['Return'] = grp['Close'].pct_change().shift(-1)

        grp = grp.dropna().reset_index(drop=True)
        if len(grp) < 120:
            continue

        X = grp[feature_cols].values
        y = grp['Return'].values

        split = int(len(grp) * (1 - test_ratio))

        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        scaler = MinMaxScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        models = {
            "Linear": LinearRegression(),
            "RandomForest": RandomForestRegressor(
                n_estimators=50,
                max_depth=6,
                min_samples_leaf=5,
                random_state=SEED,
                n_jobs=1
            ),
            "GradientBoosting": GradientBoostingRegressor(
                n_estimators=50,
                learning_rate=0.05,
                max_depth=3,
                random_state=SEED
            )
        }

        poly = PolynomialFeatures(degree=2, include_bias=False)
        X_train_poly = poly.fit_transform(X_train)
        X_test_poly = poly.transform(X_test)
        models["Polynomial"] = LinearRegression()

        for name, model in models.items():

            if name == "Polynomial":
                model.fit(X_train_poly, y_train)
                preds = model.predict(X_test_poly)
            else:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)

            actual = y_test

            signal = np.where(preds > 0, 1, -1)
            strategy_returns = signal * actual

            # ✅ Stable Sharpe
            std = np.std(strategy_returns)
            sharpe = (np.mean(strategy_returns) / (std + 1e-8) * np.sqrt(252)) if std > 0 else 0

            cumulative = (1 + strategy_returns).cumprod()
            max_dd = (cumulative / np.maximum.accumulate(cumulative) - 1).min()
            cagr = cumulative[-1] ** (252 / len(strategy_returns)) - 1

            mae = np.mean(np.abs(actual - preds))
            rmse = np.sqrt(np.mean((actual - preds) ** 2))

            metrics.append({
                'Ticker': ticker,
                'Model': name,
                'MAE': mae,
                'RMSE': rmse,
                'Sharpe': sharpe,
                'Max_Drawdown': max_dd,
                'CAGR': cagr
            })

            dates = grp['Date'].iloc[split:].reset_index(drop=True)

            all_preds.append(pd.DataFrame({
                'Date': dates,
                'Ticker': ticker,
                'Model': name,
                'Actual_Return': actual,
                'Pred_Return': preds,
                'Signal': signal,
                'Strategy_Return': strategy_returns
            }))

    if len(all_preds) == 0:
        raise ValueError("No predictions generated — check data filtering.")

    preds_df = pd.concat(all_preds, ignore_index=True)
    metrics_df = pd.DataFrame(metrics)

    preds_df.to_csv('Final Backtest Data/ml_predictions.csv', index=False)
    metrics_df.to_csv('Final Backtest Data/ml_metrics.csv', index=False)

    preds_df.to_excel('Final Backtest Data/ml_predictions.xlsx', index=False)
    metrics_df.to_excel('Final Backtest Data/ml_metrics.xlsx', index=False)

    metadata = {
        "seed": SEED,
        "test_ratio": test_ratio,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "features": feature_cols,
        "models": model_names,
        "data_hash": file_hash(BASE_DIR / "data" /  "backtestingData.csv"),
        "timestamp": datetime.now().isoformat()
    }

    with open(BASE_DIR / "results" / "metadata"/ "ml", "w") as f:
        json.dump(metadata, f, indent=4)

   
    for model_name in preds_df['Model'].unique():
        subset = preds_df[preds_df['Model'] == model_name]

        plt.figure(figsize=(10,6))
        plt.scatter(subset['Actual_Return'], subset['Pred_Return'], alpha=0.5)
        plt.xlabel('Actual Return')
        plt.ylabel('Predicted Return')
        plt.title(f'{model_name} Predicted vs Actual Returns')
        plt.grid(True)

        plt.savefig(f'Final Backtest Data/{model_name}_pred_vs_actual.png')
        plt.close()

    return metrics_df

if __name__ == '__main__':
    df = pd.read_csv(BASE_DIR / "data" /  "backtestingData.csv", parse_dates=['Date'])
    metrics = run_ml_backtest(df)

    print('\nML backtest metrics:')
    print(metrics)