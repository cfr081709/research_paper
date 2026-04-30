"""
Master backtester orchestrator.

Runs all backtesting pipelines in sequence:
  1. data_retrieval   - fetch/update price data and indicators
  2. signal_backtester  - backtest individual indicator signals
  3. ML                 - traditional ML model backtests
  4. LSTM               - LSTM neural network backtests

Usage:
  python Code/run_all_backtests.py
  
  Optional: pass start/end dates as arguments:
  python Code/run_all_backtests.py 2000-01-01 2026-01-01
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_script(script_path, description, env_vars=None):
    """Execute a Python script and report results."""
    print(f"\n{'='*70}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running: {description}")
    print(f"{'='*70}")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent.parent,  # run from researchProject root
            capture_output=False,
            text=True,
            timeout=3600  # 1 hour timeout per script
        )
        if result.returncode == 0:
            print(f"[OK] {description} completed successfully")
            return True
        else:
            print(f"[FAIL] {description} failed with exit code {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {description} timed out after 1 hour")
        return False
    except Exception as e:
        print(f"[FAIL] {description} encountered error: {e}")
        return False

def main():
    """Run all backtests in sequence."""
    code_dir = Path(__file__).parent
    
    print(f"\n{'#'*70}")
    print("# BACKTEST ORCHESTRATOR - Running all analysis pipelines")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}\n")
    
    results = {}
    
    # Step 1: Data retrieval and feature engineering
    results['data_retrieval'] = run_script(
        code_dir / 'data_retrieval.py',
        'Data Retrieval (fetch prices 2000-01-01 to 2026-01-01)'
    )
    if not results['data_retrieval']:
        print("\n[!] Data retrieval failed; halting remaining steps.")
        return
    
    # Step 2: Signal-based backtest
    results['signal_backtest'] = run_script(
        code_dir / 'signal_backtester.py',
        'Signal Backtest (individual indicator strategies)'
    )
    
    # Step 3: Traditional ML backtest
    results['ml_backtest'] = run_script(
        code_dir / 'ML.py',
        'ML Backtest (Polynomial, Linear, RandomForest, GradientBoosting)'
    )
    
    # Step 4: LSTM backtest
    results['lstm_backtest'] = run_script(
        code_dir / 'LSTM.py',
        'LSTM Backtest (Deep learning neural network)'
    )
    
    # Summary report
    print(f"\n{'='*70}")
    print("BACKTEST SUMMARY")
    print(f"{'='*70}")
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for pipeline, success in results.items():
        status = "[OK]" if success else "[FAIL]"
        print(f"  {pipeline:25s} ... {status}")
    
    print(f"\nTotal: {success_count}/{total_count} pipelines completed successfully")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Report output locations
    print("Output files generated:")
    print("  - CSV/XLSX data and metrics in: Final Backtest Data/")
    print("  - LSTM metrics: Final Backtest Data/lstm_metrics.csv / .xlsx")
    print("  - ML metrics: Final Backtest Data/ml_metrics.csv / .xlsx")
    print("  - Signal backtest: Final Backtest Data/signal_backtest_metrics.csv / .xlsx")
    print("  - Plots: Final Backtest Data/*.png")
    print()

if __name__ == '__main__':
    main()
