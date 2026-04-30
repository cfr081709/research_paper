# Machine Learning for Financial Time Series Forecasting

This project explores the predictive accuracy and trading effectiveness of multiple machine learning models applied to financial time series data. The objective is to evaluate whether statistical learning and deep learning methods can extract meaningful structure from noisy market data and translate forecasts into profitable trading strategies.

We implement and benchmark the following models within a unified backtesting framework:

- Linear Regression  
- Polynomial Regression  
- Random Forest Regression  
- Gradient Boosting Regression  
- Long Short-Term Memory (LSTM) Neural Networks  

---

## Methodology

Each model is trained to predict next-period asset returns using engineered technical indicators derived from price and volume data. A consistent feature pipeline is used across all experiments to ensure comparability.

Predictions are converted into trading signals:

- Positive predicted return → Long position  
- Negative predicted return → Short position  

A standardized backtesting engine evaluates each strategy over unseen test data.

---

## Evaluation Metrics

Model performance is assessed using both predictive and financial metrics:

### Predictive Accuracy
- Mean Absolute Error (MAE)  
- Root Mean Squared Error (RMSE)  

### Trading Performance
- Sharpe Ratio (risk-adjusted returns)  
- Compound Annual Growth Rate (CAGR)  
- Maximum Drawdown  

This dual evaluation framework ensures models are judged not only on statistical accuracy, but also on real-world trading utility.

---

## Key Objective

The study provides a comparative analysis of:

- Classical machine learning models (linear, tree-based, ensemble methods)  
- Deep learning approaches (LSTM neural networks)  

with a focus on:
- Nonlinear pattern recognition in financial markets  
- Predictive stability across assets  
- Translation of forecast accuracy into profitability  

---

## Data Access

Due to file size limitations, the full dataset is hosted externally:

Google Drive (Data Repository):  
https://drive.google.com/drive/u/1/folders/16OmyvMUsmh5zmK6HWmFDLaXkmJopb9Dq  

---

## Notes

- All experiments are implemented within a consistent backtesting framework to ensure fair comparison across models.  
- Transaction costs are not included unless otherwise specified.  
- Results are sensitive to market regime shifts and should be interpreted in that context.  

## Important Methodology Notes

### Reproducibility
All experiments use a fixed random seed (42). This ensures results can be replicated exactly.

### Signal Design Fix
Original signal logic combined trend-following and mean-reversion indicators equally,
which led to low trade frequency and poor Sharpe ratios.

This was corrected by introducing regime-awareness:
- Trend signals dominate in strong trends
- RSI signals are only used in non-trending markets

### Look-Ahead Bias
Rolling indicators (e.g., SMA200) may introduce look-ahead bias if computed globally.
This is acknowledged and discussed as a limitation.

### Additional Metrics
We report:
- Standard deviation across tickers
- Worst-performing ticker

This ensures robustness beyond aggregate Sharpe ratio.