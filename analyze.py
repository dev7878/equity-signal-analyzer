#!/usr/bin/env python3
"""
Equity Market Signal Analyzer - Main Command Line Interface
Professional equity analysis tool for global markets
"""

import argparse
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
import warnings
import pandas as pd
warnings.filterwarnings('ignore')

# Import our custom modules
from equity_data import EquityDataProvider
from signal_generator import SignalGenerator
from market_metrics import MarketMetricsCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EquityAnalyzer:
    """Main equity analysis orchestrator"""
    
    def __init__(self):
        self.data_provider = EquityDataProvider()
        self.signal_generator = SignalGenerator()
        self.metrics_calculator = MarketMetricsCalculator()
    
    def analyze_equity(self, ticker: str, start_date: str, end_date: Optional[str] = None,
                      output_dir: str = "output") -> Dict:
        """
        Perform comprehensive equity analysis
        
        Args:
            ticker: Stock ticker symbol (e.g., 'SHOP.TO')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (optional)
            output_dir: Directory to save outputs
        
        Returns:
            Dictionary with complete analysis results
        """
        logger.info(f"Starting analysis for {ticker}")
        
        # Validate ticker
        ticker_info = self.data_provider.get_ticker_info(ticker)
        if not ticker_info['supported'] and ticker != '^GSPTSE':
            logger.warning(f"Ticker {ticker} not in supported list, attempting to fetch anyway")
        
        try:
            # Fetch equity data
            logger.info("Fetching equity data...")
            equity_data = self.data_provider.fetch_equity_data(ticker, start_date, end_date)
            
            # Fetch benchmark data
            logger.info("Fetching benchmark data...")
            benchmark_data = self.data_provider.fetch_benchmark_data(start_date, end_date)
            
            # Generate signals
            logger.info("Generating trading signals...")
            equity_data_with_signals = self.signal_generator.generate_signals(equity_data)
            
            # Calculate market metrics
            logger.info("Calculating market metrics...")
            market_metrics = self.metrics_calculator.calculate_all_metrics(
                equity_data_with_signals, benchmark_data
            )
            
            # Calculate relative performance
            logger.info("Calculating relative performance...")
            relative_performance = self.data_provider.calculate_relative_performance(
                equity_data_with_signals, benchmark_data
            )
            
            # Generate attention flags
            attention_flags = self.metrics_calculator.generate_attention_flags(market_metrics)
            
            # Calculate signal accuracy
            signal_accuracy = self.signal_generator.calculate_directional_accuracy(
                equity_data_with_signals['Composite_Signal'],
                equity_data_with_signals['Returns']
            )
            
            # Compile results
            analysis_results = {
                'metadata': {
                    'ticker': ticker,
                    'ticker_info': ticker_info,
                    'analysis_date': datetime.now().isoformat(),
                    'data_period': {
                        'start_date': start_date,
                        'end_date': end_date or datetime.now().strftime('%Y-%m-%d'),
                        'total_days': len(equity_data)
                    },
                    'sector': self.data_provider.get_sector_classification(ticker)
                },
                'signals': {
                    'latest_signal': int(equity_data_with_signals['Composite_Signal'].iloc[-1]) if not pd.isna(equity_data_with_signals['Composite_Signal'].iloc[-1]) else 0,
                    'signal_breakdown': {
                        'rsi_signal': int(equity_data_with_signals['RSI_Signal'].iloc[-1]) if not pd.isna(equity_data_with_signals['RSI_Signal'].iloc[-1]) else 0,
                        'macd_signal': int(equity_data_with_signals['MACD_Signal'].iloc[-1]) if not pd.isna(equity_data_with_signals['MACD_Signal'].iloc[-1]) else 0,
                        'bollinger_signal': int(equity_data_with_signals['BB_Signal'].iloc[-1]) if not pd.isna(equity_data_with_signals['BB_Signal'].iloc[-1]) else 0,
                        'ma_signal': int(equity_data_with_signals['MA_Signal'].iloc[-1]) if not pd.isna(equity_data_with_signals['MA_Signal'].iloc[-1]) else 0,
                        'volume_signal': int(equity_data_with_signals['Volume_Signal'].iloc[-1]) if not pd.isna(equity_data_with_signals['Volume_Signal'].iloc[-1]) else 0
                    },
                    'technical_indicators': {
                        'rsi': float(equity_data_with_signals['RSI'].iloc[-1]) if not pd.isna(equity_data_with_signals['RSI'].iloc[-1]) else 50.0,
                        'macd': float(equity_data_with_signals['MACD'].iloc[-1]) if not pd.isna(equity_data_with_signals['MACD'].iloc[-1]) else 0.0,
                        'macd_signal_line': float(equity_data_with_signals['MACD_Signal'].iloc[-1]) if not pd.isna(equity_data_with_signals['MACD_Signal'].iloc[-1]) else 0.0,
                        'bb_position': float(equity_data_with_signals['BB_Position'].iloc[-1]) if not pd.isna(equity_data_with_signals['BB_Position'].iloc[-1]) else 0.5,
                        'bb_bandwidth': float(equity_data_with_signals['BB_Bandwidth'].iloc[-1]) if not pd.isna(equity_data_with_signals['BB_Bandwidth'].iloc[-1]) else 0.0
                    },
                    'directional_accuracy': signal_accuracy
                },
                'volatility_regime': {
                    'current_regime': int(equity_data_with_signals['Volatility_Regime'].iloc[-1]) if not pd.isna(equity_data_with_signals['Volatility_Regime'].iloc[-1]) else 1,
                    'regime_description': ['low', 'medium', 'high'][int(equity_data_with_signals['Volatility_Regime'].iloc[-1]) if not pd.isna(equity_data_with_signals['Volatility_Regime'].iloc[-1]) else 1],
                    'volatility_cluster': bool(equity_data_with_signals['Volatility_Cluster'].iloc[-1]) if not pd.isna(equity_data_with_signals['Volatility_Cluster'].iloc[-1]) else False
                },
                'relative_performance': {
                    'vs_benchmark_20d': float(relative_performance['Relative_Returns'].tail(20).sum() * 100) if len(relative_performance) >= 20 else None,
                    'vs_benchmark_60d': float(relative_performance['Relative_Returns'].tail(60).sum() * 100) if len(relative_performance) >= 60 else None,
                    'beta': float(relative_performance['Beta'].iloc[-1]) if 'Beta' in relative_performance.columns else None,
                    'correlation': float(relative_performance['Rolling_Correlation'].iloc[-1]) if 'Rolling_Correlation' in relative_performance.columns else None
                },
                'market_metrics': market_metrics,
                'attention_flags': attention_flags,
                'data_summary': {
                    'total_signals': int((equity_data_with_signals['Composite_Signal'] != 0).sum()),
                    'buy_signals': int((equity_data_with_signals['Composite_Signal'] == 1).sum()),
                    'sell_signals': int((equity_data_with_signals['Composite_Signal'] == -1).sum()),
                    'avg_volatility': float(equity_data_with_signals['Volatility'].mean()),
                    'max_volatility': float(equity_data_with_signals['Volatility'].max()),
                    'min_volatility': float(equity_data_with_signals['Volatility'].min())
                }
            }
            
            # Save results
            self._save_results(analysis_results, ticker, output_dir)
            
            logger.info(f"Analysis completed successfully for {ticker}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {str(e)}")
            raise
    
    def _save_results(self, results: Dict, ticker: str, output_dir: str):
        """Save analysis results to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON results
        json_filename = f"{output_dir}/{ticker.replace('.', '_')}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to {json_filename}")
        
        # Save summary to a more readable format
        summary_filename = f"{output_dir}/{ticker.replace('.', '_')}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_filename, 'w') as f:
            f.write(f"EQUITY ANALYSIS SUMMARY - {ticker}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Analysis Date: {results['metadata']['analysis_date']}\n")
            f.write(f"Ticker: {results['metadata']['ticker']}\n")
            f.write(f"Company: {results['metadata']['ticker_info']['name']}\n")
            f.write(f"Sector: {results['metadata']['sector']}\n")
            f.write(f"Data Period: {results['metadata']['data_period']['start_date']} to {results['metadata']['data_period']['end_date']}\n")
            f.write(f"Total Days: {results['metadata']['data_period']['total_days']}\n\n")
            
            f.write("SIGNALS\n")
            f.write("-" * 20 + "\n")
            signal_map = {-1: "SELL", 0: "HOLD", 1: "BUY"}
            f.write(f"Latest Signal: {signal_map[results['signals']['latest_signal']]}\n")
            f.write(f"Directional Accuracy: {results['signals']['directional_accuracy']:.2f}%\n\n")
            
            f.write("TECHNICAL INDICATORS\n")
            f.write("-" * 25 + "\n")
            indicators = results['signals']['technical_indicators']
            f.write(f"RSI: {indicators['rsi']:.2f}\n")
            f.write(f"MACD: {indicators['macd']:.4f}\n")
            f.write(f"Bollinger Position: {indicators['bb_position']:.2f}\n\n")
            
            f.write("VOLATILITY REGIME\n")
            f.write("-" * 20 + "\n")
            f.write(f"Current Regime: {results['volatility_regime']['regime_description'].upper()}\n")
            f.write(f"Volatility Cluster: {'Yes' if results['volatility_regime']['volatility_cluster'] else 'No'}\n\n")
            
            f.write("ATTENTION FLAGS\n")
            f.write("-" * 20 + "\n")
            flags = results['attention_flags']
            f.write(f"Requires Attention: {'Yes' if flags['requires_attention'] else 'No'}\n")
            f.write(f"Risk Level: {flags['risk_level'].upper()}\n")
            if flags['attention_reasons']:
                f.write("Reasons:\n")
                for reason in flags['attention_reasons']:
                    f.write(f"  - {reason}\n")
        
        logger.info(f"Summary saved to {summary_filename}")

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description='Equity Market Signal Analyzer - Professional Market Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze.py --ticker SHOP.TO --start 2023-01-01
  python analyze.py --ticker RY.TO --start 2023-01-01 --end 2023-12-31
  python analyze.py --ticker TD.TO --start 2024-01-01 --output-dir results
        """
    )
    
    parser.add_argument(
        '--ticker', '-t',
        required=True,
        help='Stock ticker symbol (e.g., SHOP.TO, RY.TO)'
    )
    
    parser.add_argument(
        '--start', '-s',
        required=True,
        help='Start date in YYYY-MM-DD format'
    )
    
    parser.add_argument(
        '--end', '-e',
        help='End date in YYYY-MM-DD format (defaults to today)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='output',
        help='Output directory for results (default: output)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate date format
    try:
        datetime.strptime(args.start, '%Y-%m-%d')
        if args.end:
            datetime.strptime(args.end, '%Y-%m-%d')
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD")
        sys.exit(1)
    
    # Create analyzer and run analysis
    analyzer = EquityAnalyzer()
    
    try:
        results = analyzer.analyze_equity(
            ticker=args.ticker,
            start_date=args.start,
            end_date=args.end,
            output_dir=args.output_dir
        )
        
        # Print summary to console
        print("\n" + "="*60)
        print(f"EQUITY ANALYSIS COMPLETE - {args.ticker}")
        print("="*60)
        
        signal_map = {-1: "SELL", 0: "HOLD", 1: "BUY"}
        print(f"Latest Signal: {signal_map[results['signals']['latest_signal']]}")
        print(f"Directional Accuracy: {results['signals']['directional_accuracy']:.2f}%")
        print(f"Volatility Regime: {results['volatility_regime']['regime_description'].upper()}")
        print(f"Requires Attention: {'Yes' if results['attention_flags']['requires_attention'] else 'No'}")
        print(f"Risk Level: {results['attention_flags']['risk_level'].upper()}")
        
        if results['attention_flags']['attention_reasons']:
            print("Attention Reasons:")
            for reason in results['attention_flags']['attention_reasons']:
                print(f"  - {reason}")
        
        print(f"\nResults saved to: {args.output_dir}/")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
