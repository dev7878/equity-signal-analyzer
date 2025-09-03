"""
Advanced Signal Generation Module for Equity Markets
Implements RSI, MACD, Bollinger Bands, and other technical indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Collection of technical indicators for equity analysis"""
    
    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band,
            'bandwidth': (upper_band - lower_band) / sma,
            'position': (prices - lower_band) / (upper_band - lower_band)
        }
    
    @staticmethod
    def moving_averages(prices: pd.Series, periods: List[int] = [5, 10, 20, 50, 200]) -> Dict[str, pd.Series]:
        """Calculate multiple moving averages"""
        ma_dict = {}
        for period in periods:
            ma_dict[f'MA_{period}'] = prices.rolling(window=period).mean()
        return ma_dict
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                   k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k_percent': k_percent,
            'd_percent': d_percent
        }
    
    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return williams_r
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr

class VolatilityAnalyzer:
    """Analyze volatility patterns and regimes"""
    
    @staticmethod
    def classify_volatility_regime(volatility: pd.Series, lookback: int = 20) -> pd.Series:
        """
        Classify volatility into low/medium/high regimes
        
        Args:
            volatility: Rolling volatility series
            lookback: Period for regime classification
        
        Returns:
            Series with regime classifications (0=low, 1=medium, 2=high)
        """
        # Calculate percentiles for regime classification
        p33 = volatility.rolling(window=lookback).quantile(0.33)
        p67 = volatility.rolling(window=lookback).quantile(0.67)
        
        regime = pd.Series(index=volatility.index, dtype=int)
        
        # Low volatility
        regime[volatility <= p33] = 0
        # Medium volatility
        regime[(volatility > p33) & (volatility <= p67)] = 1
        # High volatility
        regime[volatility > p67] = 2
        
        return regime
    
    @staticmethod
    def detect_volatility_clusters(volatility: pd.Series, threshold: float = 1.5) -> pd.Series:
        """
        Detect volatility clusters (periods of elevated volatility)
        
        Args:
            volatility: Rolling volatility series
            threshold: Z-score threshold for cluster detection
        
        Returns:
            Boolean series indicating volatility clusters
        """
        vol_mean = volatility.rolling(window=20).mean()
        vol_std = volatility.rolling(window=20).std()
        vol_zscore = (volatility - vol_mean) / vol_std
        
        return vol_zscore > threshold

class LiquidityAnalyzer:
    """Analyze liquidity patterns and volume metrics"""
    
    @staticmethod
    def volume_zscore(volume: pd.Series, period: int = 20) -> pd.Series:
        """Calculate volume z-scores"""
        vol_mean = volume.rolling(window=period).mean()
        vol_std = volume.rolling(window=period).std()
        return (volume - vol_mean) / vol_std
    
    @staticmethod
    def volume_price_trend(volume: pd.Series, price: pd.Series) -> pd.Series:
        """Calculate Volume Price Trend (VPT)"""
        price_change = price.pct_change()
        vpt = (volume * price_change).cumsum()
        return vpt
    
    @staticmethod
    def on_balance_volume(volume: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume (OBV)"""
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv

class SignalGenerator:
    """Generate trading signals based on technical analysis"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.volatility_analyzer = VolatilityAnalyzer()
        self.liquidity_analyzer = LiquidityAnalyzer()
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate comprehensive trading signals
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            DataFrame with signals and technical indicators
        """
        df = data.copy()
        
        # Calculate technical indicators
        df = self._add_technical_indicators(df)
        
        # Generate individual signals
        df = self._generate_rsi_signals(df)
        df = self._generate_macd_signals(df)
        df = self._generate_bollinger_signals(df)
        df = self._generate_ma_signals(df)
        df = self._generate_volume_signals(df)
        
        # Generate composite signal
        df = self._generate_composite_signal(df)
        
        # Add volatility and liquidity analysis
        df = self._add_volatility_analysis(df)
        df = self._add_liquidity_analysis(df)
        
        return df
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to the dataframe"""
        
        # Calculate returns first
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        # RSI
        df['RSI'] = self.indicators.rsi(df['Close'])
        
        # MACD
        macd_data = self.indicators.macd(df['Close'])
        df['MACD'] = macd_data['macd']
        df['MACD_Signal'] = macd_data['signal']
        df['MACD_Histogram'] = macd_data['histogram']
        
        # Bollinger Bands
        bb_data = self.indicators.bollinger_bands(df['Close'])
        df['BB_Upper'] = bb_data['upper']
        df['BB_Middle'] = bb_data['middle']
        df['BB_Lower'] = bb_data['lower']
        df['BB_Bandwidth'] = bb_data['bandwidth']
        df['BB_Position'] = bb_data['position']
        
        # Moving Averages
        ma_data = self.indicators.moving_averages(df['Close'])
        for key, value in ma_data.items():
            df[key] = value
        
        # Stochastic
        stoch_data = self.indicators.stochastic(df['High'], df['Low'], df['Close'])
        df['Stoch_K'] = stoch_data['k_percent']
        df['Stoch_D'] = stoch_data['d_percent']
        
        # Williams %R
        df['Williams_R'] = self.indicators.williams_r(df['High'], df['Low'], df['Close'])
        
        # ATR
        df['ATR'] = self.indicators.atr(df['High'], df['Low'], df['Close'])
        
        return df
    
    def _generate_rsi_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate RSI-based signals"""
        df['RSI_Signal'] = 0
        
        # Oversold condition (potential buy)
        df.loc[df['RSI'] < 30, 'RSI_Signal'] = 1
        
        # Overbought condition (potential sell)
        df.loc[df['RSI'] > 70, 'RSI_Signal'] = -1
        
        # RSI divergence signals
        df['RSI_Signal'] = df['RSI_Signal'].where(
            (df['RSI'] < 30) | (df['RSI'] > 70), 0
        )
        
        return df
    
    def _generate_macd_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate MACD-based signals"""
        df['MACD_Signal'] = 0
        
        # MACD line crosses above signal line (bullish)
        df.loc[(df['MACD'] > df['MACD_Signal']) & 
               (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)), 'MACD_Signal'] = 1
        
        # MACD line crosses below signal line (bearish)
        df.loc[(df['MACD'] < df['MACD_Signal']) & 
               (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)), 'MACD_Signal'] = -1
        
        return df
    
    def _generate_bollinger_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate Bollinger Bands-based signals"""
        df['BB_Signal'] = 0
        
        # Price touches lower band (potential buy)
        df.loc[df['Close'] <= df['BB_Lower'], 'BB_Signal'] = 1
        
        # Price touches upper band (potential sell)
        df.loc[df['Close'] >= df['BB_Upper'], 'BB_Signal'] = -1
        
        # Squeeze breakout signals
        df['BB_Squeeze'] = df['BB_Bandwidth'] < df['BB_Bandwidth'].rolling(20).quantile(0.1)
        
        return df
    
    def _generate_ma_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate Moving Average-based signals"""
        df['MA_Signal'] = 0
        
        # Price above multiple MAs (bullish)
        bullish_condition = (
            (df['Close'] > df['MA_5']) & 
            (df['Close'] > df['MA_10']) & 
            (df['Close'] > df['MA_20'])
        )
        
        # Price below multiple MAs (bearish)
        bearish_condition = (
            (df['Close'] < df['MA_5']) & 
            (df['Close'] < df['MA_10']) & 
            (df['Close'] < df['MA_20'])
        )
        
        df.loc[bullish_condition, 'MA_Signal'] = 1
        df.loc[bearish_condition, 'MA_Signal'] = -1
        
        return df
    
    def _generate_volume_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate volume-based signals"""
        df['Volume_Signal'] = 0
        
        # High volume with price movement
        volume_zscore = self.liquidity_analyzer.volume_zscore(df['Volume'])
        price_change = abs(df['Returns'])
        
        # High volume + significant price change
        high_volume_condition = (volume_zscore > 1.5) & (price_change > df['Returns'].rolling(20).std())
        
        df.loc[high_volume_condition & (df['Returns'] > 0), 'Volume_Signal'] = 1
        df.loc[high_volume_condition & (df['Returns'] < 0), 'Volume_Signal'] = -1
        
        return df
    
    def _generate_composite_signal(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate composite signal from all indicators"""
        signal_columns = ['RSI_Signal', 'MACD_Signal', 'BB_Signal', 'MA_Signal', 'Volume_Signal']
        
        # Calculate weighted composite signal
        weights = {'RSI_Signal': 0.25, 'MACD_Signal': 0.25, 'BB_Signal': 0.2, 
                  'MA_Signal': 0.2, 'Volume_Signal': 0.1}
        
        df['Composite_Signal'] = 0
        for signal_col in signal_columns:
            df['Composite_Signal'] += df[signal_col] * weights[signal_col]
        
        # Normalize to -1, 0, 1
        df['Composite_Signal'] = df['Composite_Signal'].apply(
            lambda x: 1 if x > 0.3 else (-1 if x < -0.3 else 0)
        )
        
        return df
    
    def _add_volatility_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility regime analysis"""
        # Only calculate if we have enough data
        if len(df) >= 20:
            df['Volatility_Regime'] = self.volatility_analyzer.classify_volatility_regime(df['Volatility'])
            df['Volatility_Cluster'] = self.volatility_analyzer.detect_volatility_clusters(df['Volatility'])
        else:
            df['Volatility_Regime'] = 1  # Default to medium
            df['Volatility_Cluster'] = False
        
        return df
    
    def _add_liquidity_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add liquidity analysis"""
        df['Volume_ZScore'] = self.liquidity_analyzer.volume_zscore(df['Volume'])
        df['VPT'] = self.liquidity_analyzer.volume_price_trend(df['Volume'], df['Close'])
        df['OBV'] = self.liquidity_analyzer.on_balance_volume(df['Volume'], df['Close'])
        
        return df
    
    def calculate_directional_accuracy(self, signals: pd.Series, returns: pd.Series, 
                                     lookforward: int = 1) -> float:
        """
        Calculate directional accuracy vs naive baseline
        
        Args:
            signals: Trading signals (-1, 0, 1)
            returns: Future returns
            lookforward: Number of periods to look forward
        
        Returns:
            Accuracy percentage
        """
        # Shift returns to align with signals
        future_returns = returns.shift(-lookforward)
        
        # Filter for non-zero signals
        signal_mask = signals != 0
        signal_returns = future_returns[signal_mask]
        signal_values = signals[signal_mask]
        
        if len(signal_returns) == 0:
            return 0.0
        
        # Calculate accuracy
        correct_predictions = (
            ((signal_values == 1) & (signal_returns > 0)) |
            ((signal_values == -1) & (signal_returns < 0))
        ).sum()
        
        total_predictions = len(signal_returns)
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        return accuracy * 100

# Example usage
if __name__ == "__main__":
    # This would typically be used with real data from equity_data.py
    print("Signal Generator module loaded successfully")
    print("Use with EquityDataProvider to generate comprehensive trading signals")
