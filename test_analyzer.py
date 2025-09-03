#!/usr/bin/env python3
"""
Test script for the Equity Market Signal Analyzer
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from equity_data import EquityDataProvider
from signal_generator import SignalGenerator
from market_metrics import MarketMetricsCalculator

def test_basic_functionality():
    """Test basic functionality of all components"""
    print("🧪 Testing Equity Signal Analyzer...")
    print("=" * 50)
    
    try:
        # Initialize components
        print("1. Initializing components...")
        data_provider = EquityDataProvider()
        signal_generator = SignalGenerator()
        metrics_calculator = MarketMetricsCalculator()
        print("✅ Components initialized successfully")
        
        # Test data fetching
        print("\n2. Testing data fetching...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        data = data_provider.fetch_equity_data('SHOP.TO', start_date, end_date)
        print(f"✅ Fetched {len(data)} records for SHOP.TO")
        
        # Test signal generation
        print("\n3. Testing signal generation...")
        data_with_signals = signal_generator.generate_signals(data)
        print(f"✅ Generated signals with {len(data_with_signals.columns)} columns")
        
        # Test metrics calculation
        print("\n4. Testing metrics calculation...")
        metrics = metrics_calculator.calculate_all_metrics(data_with_signals)
        print(f"✅ Calculated {len(metrics)} market metrics")
        
        # Test attention flags
        print("\n5. Testing attention flags...")
        flags = metrics_calculator.generate_attention_flags(metrics)
        print(f"✅ Generated attention flags: {flags['requires_attention']}")
        
        # Test signal accuracy
        print("\n6. Testing signal accuracy...")
        accuracy = signal_generator.calculate_directional_accuracy(
            data_with_signals['Composite_Signal'],
            data_with_signals['Returns']
        )
        print(f"✅ Signal accuracy: {accuracy:.2f}%")
        
        # Display sample results
        print("\n📊 Sample Results:")
        print("-" * 30)
        print(f"Latest Signal: {data_with_signals['Composite_Signal'].iloc[-1]}")
        print(f"Current RSI: {data_with_signals['RSI'].iloc[-1]:.2f}")
        print(f"Volatility Regime: {data_with_signals['Volatility_Regime'].iloc[-1]}")
        print(f"Liquidity Score: {metrics.get('liquidity_score', 0):.1f}")
        print(f"Risk Level: {flags['risk_level']}")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_tickers():
    """Test with multiple TSX tickers"""
    print("\n🔄 Testing multiple TSX tickers...")
    
    test_tickers = ['RY.TO', 'TD.TO', 'CNR.TO']
    data_provider = EquityDataProvider()
    
    for ticker in test_tickers:
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            data = data_provider.fetch_equity_data(ticker, start_date, end_date)
            print(f"✅ {ticker}: {len(data)} records")
            
        except Exception as e:
            print(f"❌ {ticker}: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Equity Signal Analyzer - Test Suite")
    print("=" * 60)
    
    # Run basic functionality test
    success = test_basic_functionality()
    
    if success:
        # Run multiple ticker test
        test_multiple_tickers()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🎯 The analyzer is ready for use.")
        print("\nNext steps:")
        print("1. Run: python analyze.py --ticker SHOP.TO --start 2023-01-01")
        print("2. Or launch dashboard: python run_dashboard.py")
    else:
        print("\n" + "=" * 60)
        print("❌ Tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
