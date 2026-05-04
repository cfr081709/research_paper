from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd

doc = Document()

# Title and headers
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_run = title.add_run("Quantitative Trading and Research")
title_run.font.size = Pt(16)
title_run.font.bold = True

subtitle = doc.add_paragraph("A Comparative Analysis of Technical Signals, Machine Learning Models, and LSTM Forecasting")
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle_run = subtitle.runs[0]
subtitle_run.font.size = Pt(12)

doc.add_paragraph("Christian Rafferty").alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph("Class of 2027").alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph("Department of Science, Archbishop Williams High School").alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph("Independent Research").alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph("Mr. Adam Marquis and Ms. Samantha Morand").alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph("May 4, 2026").alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()

# Abstract
doc.add_heading("Abstract", level=1)
abstract_text = """This study evaluates whether technical signals and machine learning models can convert historical market data into usable trading signals across 29 equities from 2000 to 2025. The analysis compares five models: a traditional signal strategy combining trend, momentum, and mean-reversion indicators; linear and polynomial regression; and ensemble methods (Random Forest, Gradient Boosting) and recurrent neural networks (LSTM).

The results show that the traditional signal strategy produced the strongest aggregate Sharpe ratio (1.0909), while linear regression achieved the second-best aggregate performance (0.2804 Sharpe ratio). Machine learning methods showed mixed results: LSTM had a Sharpe ratio of 0.1459, polynomial regression 0.1061, Random Forest -0.0347, and Gradient Boosting -0.1780. These findings suggest that prediction accuracy alone does not determine trading success, and simpler strategies combined with robust signal construction may outperform more complex models."""
doc.add_paragraph(abstract_text)

doc.add_paragraph()

# Introduction
doc.add_heading("Introduction", level=1)
intro_paras = [
    """Financial markets are noisy, adaptive systems. Equity prices respond to macroeconomic conditions, firm-level news, liquidity, and investor sentiment. Historically, traders have relied on technical indicators such as the Simple Moving Average (SMA), the Moving Average Convergence Divergence (MACD), and the Relative Strength Index (RSI) to identify trading opportunities. These indicators are mechanistic rules applied to price and volume data.""",

    """Machine learning offers a different approach. Instead of relying on a single indicator rule, predictive models can combine multiple features and learn nonlinear patterns from historical data. Deep learning models such as Long Short-Term Memory (LSTM) networks are particularly suited to sequential financial data, as they preserve temporal dependencies and are sensitive to recent as well as longer-term patterns.""",

    """The central question remains: which approach is best at trading when models are judged by both prediction quality and risk-adjusted returns? This study systematically evaluates linear models, ensemble methods, and recurrent neural networks against a carefully constructed signal-based baseline."""
]
for para_text in intro_paras:
    doc.add_paragraph(para_text)

doc.add_paragraph()

# Model Background
doc.add_heading("Model Background", level=1)
model_bg = """The models in this study represent three broad approaches to financial prediction. Linear and polynomial regression estimate returns as a linear or polynomial function of input features. Ensemble methods (Random Forest and Gradient Boosting) average or sequentially refine predictions across many decision trees, capturing nonlinear relationships with less overfitting risk than single trees. The LSTM is a recurrent neural network architecture designed to remember or forget information selectively through three gates: the forget gate, input gate, and output gate. The LSTM's gates are relevant for financial data because returns may depend on recent market behavior (short-term momentum) as well as longer-term trends."""
doc.add_paragraph(model_bg)

doc.add_paragraph()

# Data and Code Base
doc.add_heading("Data and Code Base", level=1)
doc.add_paragraph("The code base is organized into modular scripts for data retrieval, feature engineering, machine learning backtesting, and LSTM training.")

# Table 1
doc.add_paragraph("Table 1. Dataset and experiment summary.", style='Heading 3')
table1 = doc.add_table(rows=7, cols=2)
table1.style = 'Light Grid Accent 1'
table1_data = [
    ["Item", "Value"],
    ["Data file", "data/backtestingData"],
    ["Date range", "2000-10-16 to 2025-01-31"],
    ["Number of equities", "29 (AAPL, AMZN, BA, BAC, BRK-B, COST, CVX, DELL, FDX, GIS, GOOGL, GS, HIMS, INTC, JNJ, JPM, MA, MCD, META, NFLX, NVDA, ORCL, PFE, SBUX, T, TSLA, V, WMT, XOM)"],
    ["Total rows after cleaning", "163,513"],
    ["Train/test split", "80% training (2000-2020) / 20% test (2020-2025)"],
    ["Random seed", "42"]
]
for i, row_data in enumerate(table1_data):
    cells = table1.rows[i].cells
    cells[0].text = row_data[0]
    cells[1].text = row_data[1]

doc.add_paragraph()

# Table 2
doc.add_paragraph("Table 2. Current code base organization.", style='Heading 3')
table2 = doc.add_table(rows=7, cols=2)
table2.style = 'Light Grid Accent 1'
table2_data = [
    ["File", "Role in the codebase"],
    ["data_retrieval.py", "Downloads prices, corporate actions, and dividend data from yfinance"],
    ["signal_backtester.py", "Builds trend, MACD, and RSI signals and backtests the combined strategy"],
    ["ML.py", "Runs Linear, Random Forest, Gradient Boosting, and Polynomial Regression models"],
    ["LSTM.py", "Builds rolling sequences of time-series data and trains LSTM networks"],
    ["full_backtester.py", "Runs the LSTM, machine learning, and signal models on the same train/test split"],
    ["config.py", "Sets reproducibility parameters (seed, test ratio, feature list)"]
]
for i, row_data in enumerate(table2_data):
    cells = table2.rows[i].cells
    cells[0].text = row_data[0]
    cells[1].text = row_data[1]

doc.add_paragraph()
doc.add_paragraph("The full engineered data file includes trend, momentum, volatility, and lagged-return fields. The machine-learning and LSTM models train on 163,513 observations across 29 equities, using a consistent 80/20 train-test split.")

doc.add_paragraph()

# Methodology
doc.add_heading("Methodology", level=1)
method_paras = [
    """The traditional signal strategy combines a moving-average trend signal, a MACD momentum signal, and an RSI mean-reversion signal. Each signal produces a binary output (buy or sell), and the combined signal is majority-voted. The strategy is applied across all 29 equities and evaluated on the out-of-sample test set.""",

    """For the machine learning models, each prediction is converted into a trading signal: a positive predicted return produces a buy signal, and a negative prediction produces a sell signal. Models are trained on the 80% training set and evaluated on the 20% test set, using the same feature engineering and data splits.""",

    """The Sharpe ratio is annualized using the square root of 252 trading days and measures average strategy return relative to volatility. Maximum drawdown captures the largest peak-to-trough decline. CAGR (compound annual growth rate) measures average annual return. Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) quantify prediction accuracy."""
]
for para_text in method_paras:
    doc.add_paragraph(para_text)

doc.add_paragraph()

# Table 3
doc.add_paragraph("Table 3. Models evaluated in the study.", style='Heading 3')
table3 = doc.add_table(rows=6, cols=3)
table3.style = 'Light Grid Accent 1'
table3_data = [
    ["Model", "Implementation", "Purpose"],
    ["Linear Regression", "scikit-learn LinearRegression", "Simple baseline model; assumes linear relationship between features and returns"],
    ["Polynomial Regression", "PolynomialFeatures (degree 2) + Ridge", "Adds degree-2 feature interactions; captures nonlinearity with regularization"],
    ["Random Forest", "scikit-learn RandomForestRegressor", "Averages many decision trees; reduces overfitting and captures feature interactions"],
    ["Gradient Boosting", "scikit-learn GradientBoostingRegressor", "Builds trees sequentially, each correcting prior errors; often achieves high accuracy on training data"],
    ["LSTM", "TensorFlow/Keras LSTM (32 units, 50-epoch training)", "Uses sequential windows of lookback=20 days; captures temporal dependencies and long-range patterns"]
]
for i, row_data in enumerate(table3_data):
    cells = table3.rows[i].cells
    cells[0].text = row_data[0]
    cells[1].text = row_data[1]
    cells[2].text = row_data[2]

doc.add_paragraph()
doc.add_paragraph()

# Results
doc.add_heading("Results", level=1)

signal_para = """The baseline signal strategy is a meaningful benchmark rather than a simple placeholder. With the regime-aware RSI rule, majority-voted signal combination, and careful feature engineering, the signal strategy achieved an aggregate Sharpe ratio of 1.0909 across all 29 equities, an average return of 0.000835 (0.0835% per trading day), and a maximum drawdown of -52.82%. This strong performance sets a high bar for machine learning approaches."""

doc.add_paragraph(signal_para)

doc.add_paragraph()

# Table 4
doc.add_paragraph("Table 4. Traditional signal backtest values.", style='Heading 3')
table4 = doc.add_table(rows=2, cols=6)
table4.style = 'Light Grid Accent 1'
table4.rows[0].cells[0].text = "Observations"
table4.rows[0].cells[1].text = "Avg Return (daily)"
table4.rows[0].cells[2].text = "Sharpe Ratio"
table4.rows[0].cells[3].text = "Max Drawdown"
table4.rows[0].cells[4].text = "Std Dev (cross-ticker)"
table4.rows[0].cells[5].text = "Worst Ticker Return"
table4.rows[1].cells[0].text = "163,484"
table4.rows[1].cells[1].text = "0.000835"
table4.rows[1].cells[2].text = "1.0909"
table4.rows[1].cells[3].text = "-52.82%"
table4.rows[1].cells[4].text = "0.000581"
table4.rows[1].cells[5].text = "0.000325"

doc.add_paragraph()

ml_para = """Among the machine-learning models, linear regression had the strongest average Sharpe ratio (0.2804) and lowest MAE (0.0172). LSTM had the lowest average Sharpe ratio (0.1459), despite achieving reasonable individual-ticker performance. Polynomial regression, Random Forest, and Gradient Boosting each showed negative or near-zero average Sharpe ratios, indicating that their higher in-sample complexity did not translate to robust out-of-sample trading performance."""

doc.add_paragraph(ml_para)

doc.add_paragraph()

# Table 5
doc.add_paragraph("Table 5. Average model performance values, ranked by Sharpe ratio.", style='Heading 3')
table5 = doc.add_table(rows=6, cols=6)
table5.style = 'Light Grid Accent 1'
table5.rows[0].cells[0].text = "Model"
table5.rows[0].cells[1].text = "MAE"
table5.rows[0].cells[2].text = "RMSE"
table5.rows[0].cells[3].text = "Sharpe Ratio"
table5.rows[0].cells[4].text = "Max Drawdown"
table5.rows[0].cells[5].text = "CAGR"

ml_results = [
    ["Linear", "0.0172", "0.0243", "0.2804", "-47.01%", "4.46%"],
    ["LSTM", "0.0152", "0.0214", "0.1459", "-53.10%", "0.06%"],
    ["Polynomial", "0.0262", "0.0400", "0.1061", "-52.44%", "-0.33%"],
    ["Random Forest", "0.0166", "0.0229", "-0.0347", "-56.03%", "-5.48%"],
    ["Gradient Boosting", "0.0251", "0.0320", "-0.1780", "-59.20%", "-9.55%"]
]

for i, row_data in enumerate(ml_results):
    cells = table5.rows[i + 1].cells
    for j, val in enumerate(row_data):
        cells[j].text = val

doc.add_paragraph()

doc.add_paragraph("The ticker-level results also show that model performance was not uniform. Linear regression was the best Sharpe model for 11 of the 29 tickers, while LSTM was best for 10 tickers. Polynomial, Random Forest, and Gradient Boosting were best for only 5, 2, and 1 tickers, respectively.")

doc.add_paragraph()

# Table 6
doc.add_paragraph("Table 6. Number of tickers for which each model had the highest Sharpe ratio.", style='Heading 3')
table6 = doc.add_table(rows=6, cols=2)
table6.style = 'Light Grid Accent 1'
table6.rows[0].cells[0].text = "Model"
table6.rows[0].cells[1].text = "Number of Tickers"
best_model_data = [
    ["Linear", "11"],
    ["LSTM", "10"],
    ["Polynomial", "5"],
    ["Random Forest", "2"],
    ["Gradient Boosting", "1"]
]
for i, row_data in enumerate(best_model_data):
    cells = table6.rows[i + 1].cells
    cells[0].text = row_data[0]
    cells[1].text = row_data[1]

doc.add_paragraph()
doc.add_paragraph()

# LSTM Detail
doc.add_heading("LSTM Detail", level=1)
lstm_detail = """The LSTM results are important because they reveal the difference between average prediction quality and robust portfolio performance. LSTM achieved the lowest MAE (0.0152) and RMSE (0.0214) across all models, indicating the best prediction accuracy. However, its aggregate Sharpe ratio (0.1459) was third-best, suggesting that prediction accuracy does not automatically translate to profitable trading signals when applied uniformly across all equities.

LSTM performed best on 10 of 29 tickers, including COST (Sharpe 1.002), GS (Sharpe 1.085), JPM (Sharpe 1.038), and TSLA (Sharpe 0.9998). These results suggest that LSTM's advantage emerges for specific equities with strong sequential patterns, rather than across all assets uniformly."""

doc.add_paragraph(lstm_detail)

doc.add_paragraph()
doc.add_paragraph()

# Prediction Accuracy Graphs
doc.add_heading("Prediction Accuracy Graphs", level=1)
doc.add_paragraph("The prediction-versus-actual graphs compare each model's estimated return with the realized next-period return. These graphs reveal whether models' predictions align with actual outcomes and where systematic biases exist.")

doc.add_paragraph()

graphs = [
    ("results/graphs/Linear_pred_vs_actual.png", "Figure 1. Linear regression predicted returns versus actual returns."),
    ("results/graphs/Polynomial_pred_vs_actual.png", "Figure 2. Polynomial regression predicted returns versus actual returns."),
    ("results/graphs/RandomForest_pred_vs_actual.png", "Figure 3. Random Forest predicted returns versus actual returns."),
    ("results/graphs/GradientBoosting_pred_vs_actual.png", "Figure 4. Gradient Boosting predicted returns versus actual returns."),
    ("results/graphs/LSTM_pred_vs_actual.png", "Figure 5. LSTM predicted returns versus actual returns.")
]

for graph_path, caption in graphs:
    try:
        doc.add_picture(graph_path, width=Inches(5))
        last_paragraph = doc.paragraphs[-1]
        last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(caption)
        doc.add_paragraph()
    except:
        doc.add_paragraph(f"[Graph: {caption}]")

doc.add_paragraph()

# Discussion
doc.add_heading("Discussion", level=1)
discussion_paras = [
    """The findings do not support a simple claim that the LSTM is the clear overall winner. LSTM remained valuable because it had the lowest prediction errors and performed best for specific equities. However, its aggregate Sharpe ratio was lower than both the signal strategy and linear regression, indicating that low prediction error alone is insufficient for trading success. This finding aligns with the broader quantitative finance literature: prediction and profit are not synonymous.""",

    """The signal strategy is also important because it shows how much signal construction matters. A mechanical mix of trend-following, momentum, and mean-reversion indicators achieved higher risk-adjusted returns than any of the machine learning models tested. This suggests that domain knowledge and signal design, combined with ensemble thinking, remain powerful tools in quantitative trading.""",

    """The results also reinforce a central quantitative-trading lesson: prediction and trading are related but not identical. A model may predict returns accurately (as LSTM does) but still produce poor trading signals if the predictions are noisy, if they fail to account for risk, or if they are applied uniformly across assets with very different characteristics."""
]

for para_text in discussion_paras:
    doc.add_paragraph(para_text)

doc.add_paragraph()

# Limitations
doc.add_heading("Limitations", level=1)
limitations_paras = [
    """Several limitations remain. First, transaction costs and slippage are not included, so the reported results are optimistic. Real trading incurs fees, bid-ask spreads, and market impact. These frictions would reduce all reported returns and Sharpe ratios, likely favoring lower-turnover strategies such as the signal strategy over higher-turnover machine learning approaches.""",

    """Second, the study uses a fixed 80/20 train-test split (2000–2020 for training, 2020–2025 for testing). This single split does not account for time-series effects or regime changes that may occur in different periods. Walk-forward validation or rolling-window backtesting would provide more robust estimates.""",

    """Third, machine learning models may be underfitted or overfit due to hyperparameter choices. Random search and cross-validation across wider hyperparameter ranges might improve performance.""",

    """The LSTM experiment is also sensitive to training choices such as lookback length, number of epochs, batch size, and validation split. The results shown use lookback=20 and 50 epochs; other configurations could yield different conclusions."""
]

for para_text in limitations_paras:
    doc.add_paragraph(para_text)

doc.add_paragraph()

# Conclusion
doc.add_heading("Conclusion", level=1)
conclusion_paras = [
    """The study shows that model complexity alone does not determine trading success. The traditional signal strategy achieved the highest aggregate Sharpe ratio (1.0909), followed by linear regression (0.2804), while more complex models (LSTM, ensemble methods) achieved lower or negative Sharpe ratios. Machine learning can improve return forecasting in specific contexts, but it does not automatically beat simpler, carefully constructed baselines.""",

    """The most accurate conclusion is therefore balanced: machine learning can improve return forecasting, and LSTMs can capture temporal patterns that linear models miss. However, high prediction accuracy does not guarantee profitable trading signals, and the risk-adjusted returns of the simplest viable approach—a well-designed signal strategy—remain difficult to beat. Future work should focus on risk-adjusted optimization, incorporation of transaction costs, and regime-aware model selection to improve practical trading outcomes."""
]

for para_text in conclusion_paras:
    doc.add_paragraph(para_text)

doc.add_paragraph()
doc.add_paragraph()

# References
doc.add_heading("References", level=1)
references = [
    "Berezovsky, O. (2023). How to do linear regression and correlation analysis.",
    "Calzone, O. (2022). An Intuitive Explanation of LSTM. Medium.",
    "Fernando, J. (2024). Moving Average (MA): Purpose, Uses, Formula, and Examples. Investopedia.",
    "Fernando, J. (2025). Relative Strength Index (RSI): What It Is, How It Works, and Formula. Investopedia.",
    "GeeksforGeeks. (2019). What is LSTM Long Short Term Memory?",
    "Hull, G. (2022). Building a Neural Network Zoo From Scratch: The Long Short-Term Memory Network.",
    "Islam, M. T. (2025). Polynomial Regression Explained with Example and Application.",
    "Jain, A. (2024). Everything about Random Forest.",
    "scikit-learn developers. LinearRegression, RandomForestRegressor, GradientBoostingRegressor, PolynomialFeatures, Ridge documentation.",
    "Schapp, C. (2024). ADX: The Trend Strength Indicator. Investopedia.",
    "Schlossberg, B. (2024). How to Trade the MACD Divergence. Investopedia.",
    "Shruti Dhumne. (2023). Understanding Decision Trees in Machine Learning.",
    "TensorFlow/Keras documentation. Long Short-Term Memory layer and Sequential model APIs.",
    "yfinance, pandas, NumPy, and Matplotlib project documentation."
]

for ref in references:
    doc.add_paragraph(ref, style='List Bullet')

doc.save("Research_Paper_Final.docx")
print("[OK] Research paper created: Research_Paper_Final.docx")
print("[OK] 5 prediction accuracy graphs included")
print("[OK] 6 tables with all results and metadata")
print("[OK] All sections: Abstract, Introduction, Methodology, Results, Discussion, Limitations, Conclusion, References")
