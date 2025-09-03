"""
Equity Market Data Integration Module
Supports TSX tickers and provides comprehensive market data analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EquityDataProvider:
    """Handles data retrieval and processing for TSX equity markets"""
    
    def __init__(self):
        self.supported_tickers = {
            'SHOP.TO': 'Shopify Inc',
            'RY.TO': 'Royal Bank of Canada',
            'TD.TO': 'Toronto-Dominion Bank',
            'CNR.TO': 'Canadian National Railway',
            'CP.TO': 'Canadian Pacific Railway',
            'BMO.TO': 'Bank of Montreal',
            'BNS.TO': 'Bank of Nova Scotia',
            'ABX.TO': 'Barrick Gold Corporation',
            'SU.TO': 'Suncor Energy Inc',
            'ENB.TO': 'Enbridge Inc',
            'TRP.TO': 'TC Energy Corporation',
            'MFC.TO': 'Manulife Financial Corporation',
            'GWO.TO': 'Great-West Lifeco Inc',
            'SLF.TO': 'Sun Life Financial Inc',
            'ATD.TO': 'Alimentation Couche-Tard Inc',
            'WCN.TO': 'Waste Connections Inc',
            'CTC.TO': 'Canadian Tire Corporation',
            'L.TO': 'Loblaw Companies Limited',
            'MRU.TO': 'Metro Inc',
            'TFII.TO': 'TFI International Inc'
        }
        
        # TSX Composite Index for relative performance
        self.benchmark_ticker = '^GSPTSE'
        
    def get_ticker_info(self, ticker: str) -> Dict:
        """Get basic information about a ticker"""
        if ticker in self.supported_tickers:
            return {
                'ticker': ticker,
                'name': self.supported_tickers[ticker],
                'exchange': 'TSX',
                'supported': True
            }
        else:
            return {
                'ticker': ticker,
                'name': 'Unknown',
                'exchange': 'Unknown',
                'supported': False
            }
    
    def fetch_equity_data(self, ticker: str, start_date: str, end_date: Optional[str] = None, 
                         interval: str = '1d') -> pd.DataFrame:
        """
        Fetch equity data from Yahoo Finance
        
        Args:
            ticker: Stock ticker symbol (e.g., 'SHOP.TO')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (optional, defaults to today)
            interval: Data interval ('1d', '1h', '15m', etc.)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
            
            # Download data
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                raise ValueError(f"No data found for ticker {ticker}")
            
            # Clean column names (remove multi-level indexing if present)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Add derived columns
            data = self._add_derived_columns(data)
            
            logger.info(f"Successfully fetched {len(data)} records for {ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            raise
    
    def _add_derived_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add derived technical indicators to the dataframe"""
        df = data.copy()
        
        # Daily returns
        df['Returns'] = df['Close'].pct_change()
        
        # Log returns
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Daily spread proxy (High-Low %)
        df['Daily_Spread_Pct'] = ((df['High'] - df['Low']) / df['Close']) * 100
        
        # True Range
        df['TR'] = np.maximum(
            df['High'] - df['Low'],
            np.maximum(
                abs(df['High'] - df['Close'].shift(1)),
                abs(df['Low'] - df['Close'].shift(1))
            )
        )
        
        # Average True Range (14-day)
        df['ATR'] = df['TR'].rolling(window=14).mean()
        
        # Volatility (20-day rolling standard deviation)
        df['Volatility'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)
        
        return df
    
    def fetch_benchmark_data(self, start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch TSX Composite benchmark data"""
        return self.fetch_equity_data(self.benchmark_ticker, start_date, end_date)
    
    def calculate_relative_performance(self, ticker_data: pd.DataFrame, 
                                     benchmark_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate relative performance vs benchmark
        
        Args:
            ticker_data: Stock price data
            benchmark_data: Benchmark (TSX Composite) data
        
        Returns:
            DataFrame with relative performance metrics
        """
        # Align dates
        common_dates = ticker_data.index.intersection(benchmark_data.index)
        ticker_aligned = ticker_data.loc[common_dates]
        benchmark_aligned = benchmark_data.loc[common_dates]
        
        # Calculate relative performance
        relative_perf = pd.DataFrame(index=common_dates)
        relative_perf['Ticker_Returns'] = ticker_aligned['Returns']
        relative_perf['Benchmark_Returns'] = benchmark_aligned['Returns']
        relative_perf['Relative_Returns'] = relative_perf['Ticker_Returns'] - relative_perf['Benchmark_Returns']
        
        # Cumulative relative performance
        relative_perf['Cumulative_Relative_Perf'] = (1 + relative_perf['Relative_Returns']).cumprod() - 1
        
        # Rolling correlation (20-day)
        relative_perf['Rolling_Correlation'] = relative_perf['Ticker_Returns'].rolling(20).corr(
            relative_perf['Benchmark_Returns']
        )
        
        # Beta calculation (20-day rolling)
        rolling_cov = relative_perf['Ticker_Returns'].rolling(20).cov(relative_perf['Benchmark_Returns'])
        rolling_var = relative_perf['Benchmark_Returns'].rolling(20).var()
        relative_perf['Beta'] = rolling_cov / rolling_var
        
        return relative_perf
    
    def get_sector_classification(self, ticker: str) -> str:
        """Get sector classification for TSX tickers"""
        sector_map = {
            'SHOP.TO': 'Technology',
            'RY.TO': 'Financial Services',
            'TD.TO': 'Financial Services',
            'BMO.TO': 'Financial Services',
            'BNS.TO': 'Financial Services',
            'MFC.TO': 'Financial Services',
            'GWO.TO': 'Financial Services',
            'SLF.TO': 'Financial Services',
            'CNR.TO': 'Industrials',
            'CP.TO': 'Industrials',
            'ABX.TO': 'Materials',
            'SU.TO': 'Energy',
            'ENB.TO': 'Energy',
            'TRP.TO': 'Energy',
            'ATD.TO': 'Consumer Discretionary',
            'WCN.TO': 'Industrials',
            'CTC.TO': 'Consumer Discretionary',
            'L.TO': 'Consumer Staples',
            'MRU.TO': 'Consumer Staples',
            'TFII.TO': 'Industrials'
        }
        return sector_map.get(ticker, 'Unknown')
    
    def validate_ticker(self, ticker: str) -> bool:
        """Validate if ticker is supported"""
        return ticker in self.supported_tickers or ticker == self.benchmark_ticker

# Example usage and testing
if __name__ == "__main__":
    provider = EquityDataProvider()
    
    # Test with Shopify
    try:
        data = provider.fetch_equity_data('SHOP.TO', '2023-01-01', '2023-12-31')
        print(f"Data shape: {data.shape}")
        print(f"Columns: {data.columns.tolist()}")
        print(f"Latest data:\n{data.tail()}")
        
        # Test benchmark data
        benchmark = provider.fetch_benchmark_data('2023-01-01', '2023-12-31')
        print(f"Benchmark data shape: {benchmark.shape}")
        
        # Test relative performance
        rel_perf = provider.calculate_relative_performance(data, benchmark)
        print(f"Relative performance shape: {rel_perf.shape}")
        print(f"Latest relative performance:\n{rel_perf.tail()}")
        
    except Exception as e:
        print(f"Error: {e}")
