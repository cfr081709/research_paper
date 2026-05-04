from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_page_numbers(doc):
    """Add page numbers to top right of all pages (no name)"""
    section = doc.sections[0]
    footer = section.header
    footer.is_linked_to_previous = False

    paragraph = footer.paragraphs[0]
    paragraph.text = ""

    # Add page number to header
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')

    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')

    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)

    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

def set_margins(doc):
    """Set 1 inch margins"""
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

def set_double_spacing(paragraph):
    """Set paragraph to double spacing"""
    paragraph.paragraph_format.line_spacing = 2.0

def format_heading_1(doc, text):
    """Level I: centered, bolded"""
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.font.bold = True
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
    set_double_spacing(p)
    return p

def format_heading_2(doc, text):
    """Level II: left-aligned, bolded"""
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs:
        run.font.bold = True
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
    set_double_spacing(p)
    return p

def format_heading_3(doc, text):
    """Level III: left-aligned, bolded, italicized"""
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs:
        run.font.bold = True
        run.font.italic = True
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
    set_double_spacing(p)
    return p

def add_body_paragraph(doc, text):
    """Add body paragraph with proper formatting"""
    p = doc.add_paragraph(text)
    p.paragraph_format.first_line_indent = Inches(0.5)
    for run in p.runs:
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
    set_double_spacing(p)
    return p

# Create document
doc = Document()
set_margins(doc)
add_page_numbers(doc)

# Set default style for all text to Times New Roman 12pt
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)

# ===== TITLE PAGE =====
# Add blank lines for spacing
for _ in range(3):
    doc.add_paragraph()

# Title - centered, upper half of page
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_run = title.add_run("Quantitative Trading and Research: A Comparative Analysis of Technical Signals, Machine Learning Models, and LSTM Forecasting")
title_run.font.size = Pt(12)
title_run.font.name = 'Times New Roman'
title_run.font.bold = True
set_double_spacing(title)

# Add blank lines
for _ in range(4):
    doc.add_paragraph()

# Student info - centered
info_lines = [
    "Christian Rafferty",
    "Archbishop Williams High School",
    "Independent Scientific Research",
    "Mr. Adam Marquis and Ms. Samantha Morand",
    "May 4, 2026"
]

for line in info_lines:
    p = doc.add_paragraph(line)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
    set_double_spacing(p)

# Page break after title page
doc.add_page_break()

# ===== ABSTRACT =====
format_heading_1(doc, "Abstract")
doc.add_paragraph()

abstract_text = """This study investigates whether technical trading signals and machine learning models can generate profitable trading signals when applied to historical equity market data. Using 163,513 observations across 29 blue-chip equities from 2000 to 2025, this research evaluates five distinct approaches: a traditional signal strategy combining moving average, MACD, and RSI indicators; linear and polynomial regression models; ensemble methods (Random Forest and Gradient Boosting); and long short-term memory (LSTM) neural networks. Results demonstrate that the traditional signal strategy achieved the highest risk-adjusted returns with a Sharpe ratio of 1.0909, while linear regression ranked second with 0.2804. More complex models, including LSTM, achieved lower Sharpe ratios, ranging from 0.1459 to -0.1780. These findings suggest that model complexity alone does not guarantee trading success and that carefully constructed signal-based strategies may outperform sophisticated machine learning approaches when evaluated on out-of-sample data (Rafferty, 2026)."""

add_body_paragraph(doc, abstract_text)

doc.add_page_break()

# ===== INTRODUCTION =====
format_heading_1(doc, "Introduction")
doc.add_paragraph()

intro1 = """Financial markets are dynamic, noisy systems characterized by rapid price fluctuations driven by macroeconomic conditions, firm-level announcements, liquidity flows, and investor sentiment. For decades, practitioners have relied on technical indicators—such as the Simple Moving Average (SMA), Moving Average Convergence Divergence (MACD), and Relative Strength Index (RSI)—as mechanical rules to identify profitable trading opportunities (Fernando, 2024; Fernando, 2025; Schlossberg, 2024). These indicators operate on the assumption that historical price and volume patterns contain information predictive of future returns."""

add_body_paragraph(doc, intro1)

doc.add_paragraph()

intro2 = """The emergence of machine learning and artificial intelligence has introduced an alternative approach to financial prediction. Rather than applying a single indicator rule, machine learning models integrate multiple features and learn nonlinear patterns directly from data. Long Short-Term Memory (LSTM) networks, a class of recurrent neural networks, are particularly well-suited to sequential financial time series because they preserve temporal dependencies and adjust their information flow through gating mechanisms (Calzone, 2022; Hull, 2022). These models promise to capture complex patterns that simpler technical indicators may miss."""

add_body_paragraph(doc, intro2)

doc.add_paragraph()

intro3 = """Despite their theoretical appeal, machine learning models often struggle with generalization in real trading scenarios. High in-sample prediction accuracy frequently fails to translate into profitable out-of-sample trading signals, a phenomenon known as overfitting. The central research question is therefore: which approach—traditional signal construction, classical statistical models, ensemble methods, or deep learning—best generates risk-adjusted returns when evaluated on unseen market data?"""

add_body_paragraph(doc, intro3)

doc.add_paragraph()

# Hypothesis section
format_heading_2(doc, "Research Hypothesis")

hypothesis = """It is hypothesized that the LSTM model will achieve the highest risk-adjusted returns (Sharpe ratio) because its ability to capture temporal dependencies in sequential financial data will enable it to identify patterns missed by simpler approaches. The hypothesis further predicts that LSTM will substantially outperform the traditional signal strategy baseline across the test set (2020–2025) on both prediction accuracy and trading performance metrics."""

add_body_paragraph(doc, hypothesis)

doc.add_page_break()

# ===== BODY: MODEL BACKGROUND =====
format_heading_1(doc, "Model Background and Theory")
doc.add_paragraph()

format_heading_2(doc, "Technical Signal Strategy")

signal_bg = """The traditional signal strategy employed in this study combines three distinct technical indicators. The trend component uses the 50-day exponential moving average (EMA) as a long-term direction filter; prices above the EMA trigger buy signals, and prices below trigger sell signals (Fernando, 2024). The momentum component is measured using MACD, which compares the 12-day and 26-day exponential moving averages to identify trend acceleration or deceleration (Schlossberg, 2024). The mean-reversion component employs the Relative Strength Index (RSI), a bounded oscillator ranging from 0 to 100, which signals oversold conditions (RSI < 30) as potential buy signals and overbought conditions (RSI > 70) as potential sell signals (Fernando, 2025). A majority-vote rule combines these three independent signals into a unified trading decision, reducing false signals from any single indicator (Rafferty, 2026)."""

add_body_paragraph(doc, signal_bg)

doc.add_paragraph()

format_heading_2(doc, "Linear and Polynomial Regression")

linear_bg = """Linear regression models the conditional expectation of stock returns as a linear function of input features. The model minimizes the sum of squared residuals and produces interpretable coefficients for each feature, enabling practitioners to understand the direction and magnitude of each feature's contribution to price prediction. Polynomial regression extends this approach by introducing degree-2 interactions and nonlinear terms, allowing the model to fit more complex relationships at the cost of increased parameters and potential overfitting (Islam, 2025)."""

add_body_paragraph(doc, linear_bg)

doc.add_paragraph()

format_heading_2(doc, "Ensemble Methods: Random Forest and Gradient Boosting")

ensemble_bg = """Random Forest combines predictions from many independent decision trees, each trained on random subsets of features and observations. This ensemble averaging reduces variance and overfitting relative to single trees while capturing nonlinear relationships (Jain, 2024). Gradient Boosting, by contrast, builds trees sequentially, with each new tree correcting errors from prior trees. This sequential refinement often achieves high in-sample accuracy but carries elevated risk of overfitting when test data distributions shift (Shruti Dhumne, 2023)."""

add_body_paragraph(doc, ensemble_bg)

doc.add_paragraph()

format_heading_2(doc, "Long Short-Term Memory Neural Networks")

lstm_bg = """The LSTM is a recurrent neural network architecture designed to address the vanishing gradient problem inherent in standard recurrent networks. LSTM units contain three gating mechanisms: the forget gate, which controls information retention from prior time steps; the input gate, which regulates the addition of new information; and the output gate, which determines what information is exposed to downstream layers (GeeksforGeeks, 2019; Calzone, 2022). These gates enable LSTMs to preserve long-range dependencies crucial for financial time series, where returns may depend on both recent momentum and longer-term trends. In this study, LSTM models are trained on rolling 20-day sequences of engineered features, with lookback windows allowing the network to learn temporal patterns (Rafferty, 2026)."""

add_body_paragraph(doc, lstm_bg)

doc.add_page_break()

# ===== BODY: DATA AND METHODOLOGY =====
format_heading_1(doc, "Data and Methodology")
doc.add_paragraph()

format_heading_2(doc, "Dataset Description")

dataset_para = """The analysis employs 25 years of daily price and volume data spanning October 16, 2000, through January 31, 2025, across 29 blue-chip equities: AAPL, AMZN, BA, BAC, BRK-B, COST, CVX, DELL, FDX, GIS, GOOGL, GS, HIMS, INTC, JNJ, JPM, MA, MCD, META, NFLX, NVDA, ORCL, PFE, SBUX, T, TSLA, V, WMT, and XOM. After removing missing values and corporate action adjustments, the cleaned dataset contains 163,513 daily observations. The data are split into an 80% training set (2000–2020, 163,513 observations) and a 20% held-out test set (2020–2025), ensuring temporal ordering is preserved and preventing look-ahead bias (Rafferty, 2026)."""

add_body_paragraph(doc, dataset_para)

doc.add_paragraph()

format_heading_2(doc, "Feature Engineering")

features_para = """All models train on a consistent feature set comprising nine engineered variables: Open, High, Low, Close, and Volume prices; the 20-day and 50-day exponential moving averages (EMA_20, EMA_50); the 14-day Relative Strength Index (RSI_14); and the Moving Average Convergence Divergence (MACD). These features capture price levels, volatility, trend, momentum, and mean-reversion signals. Each feature is lagged by one trading day to ensure predictions represent next-day returns without look-ahead bias (Rafferty, 2026)."""

add_body_paragraph(doc, features_para)

doc.add_paragraph()

format_heading_2(doc, "Model Training and Evaluation")

eval_para = """All machine learning models employ a consistent 80/20 train-test split with random seed 42 for reproducibility. Linear regression is trained using scikit-learn's ordinary least squares estimator. Polynomial features are generated with degree 2 and regularized with Ridge regression to mitigate overfitting. Random Forest and Gradient Boosting models use scikit-learn's default hyperparameters (100 trees, max depth unlimited). The LSTM is implemented in TensorFlow/Keras with a 32-unit hidden layer, trained for 50 epochs on rolling sequences of 20-day lookback windows. All models are evaluated on the held-out test set using three metrics: Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) quantify prediction accuracy, while the annualized Sharpe ratio measures risk-adjusted trading returns using the square root of 252 trading days (Rafferty, 2026)."""

add_body_paragraph(doc, eval_para)

doc.add_paragraph()

format_heading_2(doc, "Signal Generation and Backtesting")

signal_para = """For machine learning models, each predicted return is converted into a trading signal: positive predictions trigger buy orders, negative predictions trigger sell orders. Buy signals are held for one trading day, after which the position is liquidated. The traditional signal strategy generates signals from the majority vote of trend, momentum, and mean-reversion indicators using the same buy-and-hold-for-one-day convention. All strategies are evaluated on the out-of-sample test set, with performance measured by Sharpe ratio (risk-adjusted return), maximum drawdown (largest peak-to-trough decline), and compound annual growth rate (CAGR). The Sharpe ratio is computed as annualized return divided by annualized volatility, standardizing comparisons across different risk levels (Rafferty, 2026)."""

add_body_paragraph(doc, signal_para)

doc.add_page_break()

# ===== RESULTS =====
format_heading_1(doc, "Results")
doc.add_paragraph()

format_heading_2(doc, "Signal Strategy Performance")

signal_results = """The traditional signal strategy serves as a meaningful performance baseline. Across all 29 equities in the test set (2020–2025), the majority-voted signal combination achieved an aggregate Sharpe ratio of 1.0909, substantially outperforming all machine learning approaches. The strategy generated an average daily return of 0.000835 (approximately 0.0835% per trading day, or roughly 21% annualized), with a maximum drawdown of −52.82%. These metrics reflect the strategy's strong sensitivity to trend-following and momentum, combined with mean-reversion filtering through RSI. The signal strategy's success demonstrates that domain knowledge, indicator engineering, and ensemble signal construction remain powerful tools in algorithmic trading (Rafferty, 2026)."""

add_body_paragraph(doc, signal_results)

doc.add_paragraph()

format_heading_2(doc, "Machine Learning Model Performance")

ml_results1 = """Among the five machine learning approaches evaluated, linear regression achieved the second-highest aggregate Sharpe ratio of 0.2804, with the lowest MAE (0.0172) and RMSE (0.0243) across all 29 equities. This finding indicates that the linear model captures systematic price movements while avoiding the overfitting that often accompanies more complex approaches. The LSTM achieved the third-best Sharpe ratio (0.1459), the lowest overall MAE (0.0152), and the lowest RMSE (0.0214). Although the LSTM demonstrated the most accurate predictions in absolute terms, its superior prediction accuracy did not translate into correspondingly superior risk-adjusted trading returns (Rafferty, 2026)."""

add_body_paragraph(doc, ml_results1)

doc.add_paragraph()

ml_results2 = """Polynomial regression achieved a Sharpe ratio of 0.1061, while Random Forest and Gradient Boosting produced negative Sharpe ratios of −0.0347 and −0.1780, respectively. These results suggest that increased model complexity—whether through polynomial feature interactions or tree ensembles—does not guarantee improved out-of-sample performance. Rather, the more complex models appear to have overfit the training data, learning spurious patterns that do not generalize to the test period. The ranking of models by Sharpe ratio is therefore: (1) Signal Strategy (1.0909), (2) Linear (0.2804), (3) LSTM (0.1459), (4) Polynomial (0.1061), (5) Random Forest (−0.0347), and (6) Gradient Boosting (−0.1780) (Rafferty, 2026)."""

add_body_paragraph(doc, ml_results2)

doc.add_paragraph()

format_heading_2(doc, "Ticker-Level Analysis")

ticker_results = """Results at the individual equity level reveal substantial heterogeneity across instruments. Linear regression was the best-performing model (highest Sharpe ratio) for 11 of 29 equities, while LSTM was best for 10 equities. Polynomial regression was best for 5 equities, Random Forest for 2, and Gradient Boosting for only 1 equity. LSTM's best performances were concentrated in equities with strong trend-following characteristics, including COST (Sharpe 1.002), GS (Sharpe 1.085), JPM (Sharpe 1.038), and TSLA (Sharpe 0.9998). These results suggest that LSTM's temporal learning is particularly effective for certain asset classes but does not provide universal improvement across all equities (Rafferty, 2026)."""

add_body_paragraph(doc, ticker_results)

doc.add_paragraph()

format_heading_2(doc, "Prediction Accuracy versus Trading Performance")

pred_results = """A critical finding is the disconnect between prediction accuracy and trading profitability. LSTM achieved the lowest prediction error (MAE 0.0152, RMSE 0.0214) but only the third-best Sharpe ratio. Conversely, Linear regression had the fourth-lowest MAE (0.0172) but the second-best Sharpe ratio. This discrepancy arises because accurate predictions do not automatically yield profitable trading signals when predictions are noisy, correlate with volatility, or apply uniformly to heterogeneous assets. The results highlight a central lesson in quantitative finance: reducing prediction error is necessary but not sufficient for trading success (Rafferty, 2026)."""

add_body_paragraph(doc, pred_results)

doc.add_page_break()

# ===== DISCUSSION =====
format_heading_1(doc, "Discussion")
doc.add_paragraph()

discuss1 = """The hypothesis that LSTM would achieve the highest risk-adjusted returns is not supported by the data. Instead, the traditional signal strategy and linear regression substantially outperformed LSTM and more complex models. LSTM's failure to produce superior out-of-sample returns—despite achieving the lowest prediction errors—demonstrates that prediction accuracy alone is insufficient for trading success. This finding aligns with established literature showing that overfitting, noise in predictions, and regime changes often undermine sophisticated models (Rafferty, 2026)."""

add_body_paragraph(doc, discuss1)

doc.add_paragraph()

discuss2 = """The superior performance of the signal strategy reveals the importance of domain knowledge and feature engineering in quantitative trading. The majority-vote combination of trend, momentum, and mean-reversion indicators achieved a Sharpe ratio of 1.0909, substantially higher than any machine learning alternative. This result suggests that financial domain expertise, encoded in carefully designed technical indicators, remains a powerful alternative to learned models. The signal strategy's robustness may stem from its interpretability and its reliance on economic principles (trend persistence, momentum, mean reversion) rather than spurious correlations discovered by machine learning (Rafferty, 2026)."""

add_body_paragraph(doc, discuss2)

doc.add_paragraph()

discuss3 = """Linear regression's second-place finish is particularly noteworthy. Among machine learning approaches, the simplest model outperformed more complex alternatives. This outcome is consistent with the bias-variance tradeoff: complex models reduce bias but increase variance, leading to overfitting on the training set and poor generalization on test data. Linear regression's parsimony—fewer parameters to estimate—reduces overfitting risk and may enable better generalization to out-of-sample periods with different market regimes (Rafferty, 2026)."""

add_body_paragraph(doc, discuss3)

doc.add_paragraph()

discuss4 = """The poor performance of Gradient Boosting and Random Forest highlights the risk of ensemble overfitting in algorithmic trading. While these methods can achieve high training accuracy, their flexibility enables them to fit noise and exploit spurious patterns present only in historical data. The negative Sharpe ratios indicate that these models not only failed to generate excess returns but actually underperformed the buy-and-hold baseline, suggesting systematic overfitting (Rafferty, 2026)."""

add_body_paragraph(doc, discuss4)

doc.add_paragraph()

format_heading_2(doc, "Implications for Quantitative Trading")

implications = """These findings carry practical implications for traders and portfolio managers. First, model complexity and prediction accuracy are not reliable proxies for trading profitability. Second, domain knowledge and signal construction—rooted in economic principles and behavioral finance—may provide more robust guidance than purely data-driven approaches. Third, single models should not be deployed without rigorous out-of-sample validation; the poor performance of Gradient Boosting and Random Forest demonstrates how easily sophisticated models can fail in live trading. Finally, portfolio managers should consider hybrid approaches that combine multiple signal sources, as the traditional strategy's success partly derives from its integration of multiple indicators rather than reliance on a single feature (Rafferty, 2026)."""

add_body_paragraph(doc, implications)

doc.add_paragraph()

format_heading_2(doc, "Limitations")

lim1 = """This study has several limitations that constrain the generalizability of findings. First, transaction costs, market impact, and bid-ask spreads are not included in the analysis. Real trading incurs fees that would substantially reduce all reported returns and Sharpe ratios. Low-frequency strategies (such as the signal strategy) would be less affected than high-turnover machine learning approaches, potentially amplifying the relative advantage of simpler methods. Future research should incorporate realistic cost assumptions (Rafferty, 2026)."""

add_body_paragraph(doc, lim1)

doc.add_paragraph()

lim2 = """Second, the study employs a single fixed train-test split (2000–2020 training, 2020–2025 testing). This structure does not account for multiple market regimes, structural breaks, or the adaptive nature of financial markets. Walk-forward validation or rolling-window backtesting, in which training windows slide forward in time, would provide more robust estimates of out-of-sample performance (Rafferty, 2026)."""

add_body_paragraph(doc, lim2)

doc.add_paragraph()

lim3 = """Third, machine learning hyperparameters may not be optimally tuned. Extensive grid search and cross-validation across wider hyperparameter ranges might improve model performance; the current results reflect reasonable default configurations rather than exhaustive optimization (Rafferty, 2026)."""

add_body_paragraph(doc, lim3)

doc.add_paragraph()

lim4 = """Finally, the LSTM architecture employed uses a fixed lookback window of 20 days and 50 training epochs. Alternative configurations—longer lookback windows, deeper networks, different batch sizes, or different optimization algorithms—might yield superior performance. The LSTM results are thus sensitive to these design choices (Rafferty, 2026)."""

add_body_paragraph(doc, lim4)

doc.add_page_break()

# ===== CONCLUSION =====
format_heading_1(doc, "Conclusion")
doc.add_paragraph()

conclusion = """This study evaluated whether technical signals and machine learning models can generate profitable trading signals across 29 equities over 25 years of market data. The research hypothesis—that LSTM neural networks would achieve the highest risk-adjusted returns due to their ability to capture temporal patterns—is not supported by the data. Instead, the traditional signal strategy achieved a Sharpe ratio of 1.0909, substantially outperforming linear regression (0.2804), LSTM (0.1459), polynomial regression (0.1061), Random Forest (−0.0347), and Gradient Boosting (−0.1780). These findings suggest three conclusions. First, model complexity does not guarantee trading success; simpler approaches often generalize better to unseen data. Second, domain knowledge and careful signal construction remain powerful tools in algorithmic trading, potentially outperforming purely data-driven approaches. Third, prediction accuracy and trading profitability are distinct objectives; low prediction error does not automatically yield profitable trading signals. Future research should incorporate transaction costs, employ walk-forward validation across multiple market regimes, and explore hybrid models that integrate domain knowledge with machine learning. The most important takeaway is that quantitative traders must validate all approaches rigorously on out-of-sample data before deployment, as historical performance is no guarantee of future results (Rafferty, 2026)."""

add_body_paragraph(doc, conclusion)

doc.add_page_break()

# ===== REFERENCES =====
format_heading_1(doc, "References")
doc.add_paragraph()

references = [
    "Calzone, O. (2022). An intuitive explanation of LSTM. Medium.",
    "Fernando, J. (2024). Moving average (MA): Purpose, uses, formula, and examples. Investopedia.",
    "Fernando, J. (2025). Relative strength index (RSI): What it is, how it works, and formula. Investopedia.",
    "GeeksforGeeks. (2019). What is LSTM long short term memory? Retrieved from https://www.geeksforgeeks.org/",
    "Hull, G. (2022). Building a neural network zoo from scratch: The long short-term memory network.",
    "Islam, M. T. (2025). Polynomial regression explained with example and application.",
    "Jain, A. (2024). Everything about random forest. Towards Data Science.",
    "Rafferty, C. (2026). Quantitative trading and research: A comparative analysis of technical signals, machine learning models, and LSTM forecasting. Independent Scientific Research, Archbishop Williams High School.",
    "Schlossberg, B. (2024). How to trade the MACD divergence. Investopedia.",
    "Shruti Dhumne. (2023). Understanding decision trees in machine learning. Towards Data Science.",
]

# Sort alphabetically
references.sort()

for ref in references:
    p = doc.add_paragraph(ref)
    p.paragraph_format.left_indent = Inches(0)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    for run in p.runs:
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
    set_double_spacing(p)

doc.save("Research_Paper_APA_Format.docx")
print("[OK] APA-formatted research paper created: Research_Paper_APA_Format.docx")
print("[OK] Title page with proper formatting")
print("[OK] Abstract, Introduction (with hypothesis), Body sections, Discussion, Limitations, Conclusion")
print("[OK] In-text citations (Last name, Year) throughout")
print("[OK] References page (alphabetized, hanging indent)")
print("[OK] Times New Roman 12pt, double-spaced, 1 inch margins")
print("[OK] Level I-II headings properly formatted")
