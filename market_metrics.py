"""
Equity Market Metrics Module
Provides comprehensive market analytics including spreads, volatility, and liquidity metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MarketMetricsCalculator:
    """Calculate comprehensive equity market metrics for analysis"""
    
    def __init__(self):
        self.metrics_cache = {}
    
    def calculate_all_metrics(self, data: pd.DataFrame, benchmark_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Calculate all market metrics for a given equity
        
        Args:
            data: OHLCV data for the equity
            benchmark_data: Optional benchmark data for relative metrics
        
        Returns:
            Dictionary containing all calculated metrics
        """
        metrics = {}
        
        # Basic price metrics
        metrics.update(self._calculate_price_metrics(data))
        
        # Volatility metrics
        metrics.update(self._calculate_volatility_metrics(data))
        
        # Liquidity metrics
        metrics.update(self._calculate_liquidity_metrics(data))
        
        # Spread metrics
        metrics.update(self._calculate_spread_metrics(data))
        
        # Risk metrics
        metrics.update(self._calculate_risk_metrics(data))
        
        # Relative performance metrics (if benchmark provided)
        if benchmark_data is not None:
            metrics.update(self._calculate_relative_metrics(data, benchmark_data))
        
        # Market quality metrics
        metrics.update(self._calculate_market_quality_metrics(data))
        
        return metrics
    
    def _calculate_price_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate basic price-based metrics"""
        latest = data.iloc[-1]
        metrics = {}
        
        # Price levels
        metrics['current_price'] = float(latest['Close'])
        metrics['daily_high'] = float(latest['High'])
        metrics['daily_low'] = float(latest['Low'])
        metrics['daily_open'] = float(latest['Open'])
        
        # Price changes
        metrics['daily_change'] = float(latest['Close'] - latest['Open'])
        metrics['daily_change_pct'] = float((latest['Close'] - latest['Open']) / latest['Open'] * 100)
        
        # Price ranges
        metrics['daily_range'] = float(latest['High'] - latest['Low'])
        metrics['daily_range_pct'] = float((latest['High'] - latest['Low']) / latest['Close'] * 100)
        
        # Recent performance
        if len(data) >= 5:
            metrics['week_change_pct'] = float((latest['Close'] - data.iloc[-5]['Close']) / data.iloc[-5]['Close'] * 100)
        
        if len(data) >= 20:
            metrics['month_change_pct'] = float((latest['Close'] - data.iloc[-20]['Close']) / data.iloc[-20]['Close'] * 100)
        
        if len(data) >= 252:
            metrics['year_change_pct'] = float((latest['Close'] - data.iloc[-252]['Close']) / data.iloc[-252]['Close'] * 100)
        
        return metrics
    
    def _calculate_volatility_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate volatility-related metrics"""
        metrics = {}
        
        # Historical volatility
        returns = data['Close'].pct_change().dropna()
        
        if len(returns) >= 20:
            # 20-day volatility (annualized)
            metrics['volatility_20d'] = float(returns.tail(20).std() * np.sqrt(252) * 100)
            
            # 60-day volatility (annualized)
            if len(returns) >= 60:
                metrics['volatility_60d'] = float(returns.tail(60).std() * np.sqrt(252) * 100)
            
            # Volatility percentiles
            vol_20d_series = returns.rolling(20).std() * np.sqrt(252) * 100
            current_vol = vol_20d_series.iloc[-1]
            vol_percentile = stats.percentileofscore(vol_20d_series.dropna(), current_vol)
            metrics['volatility_percentile'] = float(vol_percentile)
            
            # Volatility regime classification
            vol_mean = vol_20d_series.mean()
            vol_std = vol_20d_series.std()
            
            if current_vol < vol_mean - vol_std:
                metrics['volatility_regime'] = 'low'
            elif current_vol > vol_mean + vol_std:
                metrics['volatility_regime'] = 'high'
            else:
                metrics['volatility_regime'] = 'medium'
        
        # Realized volatility vs implied volatility proxy
        if 'ATR' in data.columns:
            atr_pct = (data['ATR'].iloc[-1] / data['Close'].iloc[-1]) * 100
            metrics['atr_percentage'] = float(atr_pct)
        
        return metrics
    
    def _calculate_liquidity_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate liquidity-related metrics"""
        metrics = {}
        
        # Volume metrics
        latest_volume = data['Volume'].iloc[-1]
        metrics['daily_volume'] = int(latest_volume) if not pd.isna(latest_volume) else 0
        
        if len(data) >= 20:
            avg_volume_20d = data['Volume'].tail(20).mean()
            metrics['avg_volume_20d'] = int(avg_volume_20d) if not pd.isna(avg_volume_20d) else 0
            if avg_volume_20d > 0 and not pd.isna(latest_volume):
                metrics['volume_ratio'] = float(latest_volume / avg_volume_20d)
            else:
                metrics['volume_ratio'] = 1.0
            
            # Volume z-score
            volume_mean = data['Volume'].tail(20).mean()
            volume_std = data['Volume'].tail(20).std()
            if volume_std > 0 and not pd.isna(volume_mean) and not pd.isna(latest_volume):
                metrics['volume_zscore'] = float((latest_volume - volume_mean) / volume_std)
            else:
                metrics['volume_zscore'] = 0.0
        
        # Dollar volume
        if not pd.isna(latest_volume) and not pd.isna(data['Close'].iloc[-1]):
            metrics['dollar_volume'] = float(latest_volume * data['Close'].iloc[-1])
        else:
            metrics['dollar_volume'] = 0.0
        
        # Volume-weighted average price (VWAP) for recent period
        if len(data) >= 20:
            volume_sum = data['Volume'].tail(20).sum()
            if volume_sum > 0 and not pd.isna(volume_sum):
                vwap = (data['Close'] * data['Volume']).tail(20).sum() / volume_sum
                metrics['vwap_20d'] = float(vwap) if not pd.isna(vwap) else 0.0
                if vwap > 0 and not pd.isna(data['Close'].iloc[-1]):
                    metrics['price_vs_vwap'] = float((data['Close'].iloc[-1] - vwap) / vwap * 100)
                else:
                    metrics['price_vs_vwap'] = 0.0
            else:
                metrics['vwap_20d'] = 0.0
                metrics['price_vs_vwap'] = 0.0
        
        # Liquidity score (composite metric)
        liquidity_score = 0
        if 'volume_ratio' in metrics:
            liquidity_score += min(metrics['volume_ratio'], 3) / 3 * 40  # Up to 40 points
        if 'volume_zscore' in metrics:
            liquidity_score += max(0, min(metrics['volume_zscore'], 3)) / 3 * 30  # Up to 30 points
        if 'daily_range_pct' in metrics:
            # Lower range = higher liquidity (more stable)
            liquidity_score += max(0, (5 - metrics['daily_range_pct']) / 5 * 30)  # Up to 30 points
        
        metrics['liquidity_score'] = float(min(liquidity_score, 100))
        
        return metrics
    
    def _calculate_spread_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate spread-related metrics (proxy for bid-ask spreads)"""
        metrics = {}
        
        # Daily spread proxy (High-Low as % of close)
        daily_spread = (data['High'] - data['Low']) / data['Close'] * 100
        metrics['daily_spread_pct'] = float(daily_spread.iloc[-1])
        
        if len(data) >= 20:
            # Average spread over 20 days
            metrics['avg_spread_20d'] = float(daily_spread.tail(20).mean())
            
            # Spread volatility
            metrics['spread_volatility'] = float(daily_spread.tail(20).std())
            
            # Spread percentile
            spread_percentile = stats.percentileofscore(daily_spread.dropna(), daily_spread.iloc[-1])
            metrics['spread_percentile'] = float(spread_percentile)
        
        # Effective spread proxy (using intraday volatility)
        if 'ATR' in data.columns:
            effective_spread = (data['ATR'].iloc[-1] / data['Close'].iloc[-1]) * 100
            metrics['effective_spread_pct'] = float(effective_spread)
        
        return metrics
    
    def _calculate_risk_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate risk-related metrics"""
        metrics = {}
        
        returns = data['Close'].pct_change().dropna()
        
        if len(returns) >= 20:
            # Value at Risk (VaR) - 5% VaR
            var_5 = np.percentile(returns, 5)
            metrics['var_5pct'] = float(var_5 * 100)
            
            # Expected Shortfall (Conditional VaR)
            es_5 = returns[returns <= var_5].mean()
            metrics['expected_shortfall_5pct'] = float(es_5 * 100)
            
            # Maximum Drawdown
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            metrics['max_drawdown'] = float(drawdown.min() * 100)
            
            # Sharpe Ratio (assuming risk-free rate of 2%)
            risk_free_rate = 0.02 / 252  # Daily risk-free rate
            excess_returns = returns - risk_free_rate
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252)
            metrics['sharpe_ratio'] = float(sharpe_ratio)
            
            # Sortino Ratio
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 0:
                downside_std = downside_returns.std()
                sortino_ratio = excess_returns.mean() / downside_std * np.sqrt(252)
                metrics['sortino_ratio'] = float(sortino_ratio)
            else:
                metrics['sortino_ratio'] = float('inf')
        
        return metrics
    
    def _calculate_relative_metrics(self, data: pd.DataFrame, benchmark_data: pd.DataFrame) -> Dict:
        """Calculate relative performance metrics vs benchmark"""
        metrics = {}
        
        # Align dates
        common_dates = data.index.intersection(benchmark_data.index)
        if len(common_dates) < 2:
            return metrics
        
        equity_aligned = data.loc[common_dates]
        benchmark_aligned = benchmark_data.loc[common_dates]
        
        # Calculate returns
        equity_returns = equity_aligned['Close'].pct_change().dropna()
        benchmark_returns = benchmark_aligned['Close'].pct_change().dropna()
        
        # Align returns
        common_return_dates = equity_returns.index.intersection(benchmark_returns.index)
        equity_returns = equity_returns.loc[common_return_dates]
        benchmark_returns = benchmark_returns.loc[common_return_dates]
        
        if len(equity_returns) < 20:
            return metrics
        
        # Relative performance
        relative_returns = equity_returns - benchmark_returns
        metrics['relative_return_20d'] = float(relative_returns.tail(20).sum() * 100)
        metrics['relative_return_60d'] = float(relative_returns.tail(60).sum() * 100) if len(relative_returns) >= 60 else None
        
        # Beta calculation
        covariance = np.cov(equity_returns.tail(60), benchmark_returns.tail(60))[0, 1]
        benchmark_variance = np.var(benchmark_returns.tail(60))
        if benchmark_variance > 0:
            beta = covariance / benchmark_variance
            metrics['beta'] = float(beta)
        
        # Correlation
        correlation = np.corrcoef(equity_returns.tail(60), benchmark_returns.tail(60))[0, 1]
        metrics['correlation_60d'] = float(correlation)
        
        # Information Ratio
        tracking_error = relative_returns.std() * np.sqrt(252)
        if tracking_error > 0:
            information_ratio = relative_returns.mean() * 252 / tracking_error
            metrics['information_ratio'] = float(information_ratio)
        
        # Alpha (CAPM)
        if 'beta' in metrics:
            risk_free_rate = 0.02
            market_return = benchmark_returns.mean() * 252
            expected_return = risk_free_rate + metrics['beta'] * (market_return - risk_free_rate)
            actual_return = equity_returns.mean() * 252
            alpha = actual_return - expected_return
            metrics['alpha'] = float(alpha * 100)
        
        return metrics
    
    def _calculate_market_quality_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate market quality metrics"""
        metrics = {}
        
        # Price efficiency (how well price follows random walk)
        returns = data['Close'].pct_change().dropna()
        if len(returns) >= 20:
            # Autocorrelation (should be close to 0 for efficient markets)
            autocorr = returns.autocorr(lag=1)
            metrics['price_efficiency'] = float(1 - abs(autocorr))  # Higher = more efficient
        
        # Market impact proxy (using volume vs price change relationship)
        if len(data) >= 20:
            volume_changes = data['Volume'].pct_change().dropna()
            price_changes = abs(data['Close'].pct_change().dropna())
            
            # Align the series
            common_dates = volume_changes.index.intersection(price_changes.index)
            if len(common_dates) >= 10:
                volume_changes = volume_changes.loc[common_dates]
                price_changes = price_changes.loc[common_dates]
                
                # Correlation between volume and price changes
                vol_price_corr = np.corrcoef(volume_changes, price_changes)[0, 1]
                metrics['market_impact_proxy'] = float(vol_price_corr)
        
        # Price stability (inverse of volatility)
        if 'volatility_20d' in self._calculate_volatility_metrics(data):
            vol_metrics = self._calculate_volatility_metrics(data)
            stability = max(0, 100 - vol_metrics['volatility_20d'])
            metrics['price_stability'] = float(stability)
        
        return metrics
    
    def generate_attention_flags(self, metrics: Dict) -> Dict:
        """
        Generate attention flags for unusual market conditions
        
        Args:
            metrics: Dictionary of calculated metrics
        
        Returns:
            Dictionary with attention flags
        """
        flags = {
            'requires_attention': False,
            'attention_reasons': [],
            'risk_level': 'low'
        }
        
        # High volatility flag
        if metrics.get('volatility_20d', 0) > 40:
            flags['requires_attention'] = True
            flags['attention_reasons'].append('High volatility detected')
            flags['risk_level'] = 'high'
        
        # Unusual volume flag
        if metrics.get('volume_ratio', 1) > 3:
            flags['requires_attention'] = True
            flags['attention_reasons'].append('Unusual volume spike')
        
        # Large price movement flag
        if abs(metrics.get('daily_change_pct', 0)) > 10:
            flags['requires_attention'] = True
            flags['attention_reasons'].append('Large daily price movement')
            flags['risk_level'] = 'high'
        
        # High spread flag
        if metrics.get('daily_spread_pct', 0) > 5:
            flags['requires_attention'] = True
            flags['attention_reasons'].append('Wide bid-ask spread proxy')
        
        # Low liquidity flag
        if metrics.get('liquidity_score', 100) < 30:
            flags['requires_attention'] = True
            flags['attention_reasons'].append('Low liquidity detected')
        
        # High drawdown flag
        if metrics.get('max_drawdown', 0) < -20:
            flags['requires_attention'] = True
            flags['attention_reasons'].append('Significant drawdown')
            flags['risk_level'] = 'high'
        
        # Update risk level based on multiple factors
        risk_factors = 0
        if metrics.get('volatility_20d', 0) > 30:
            risk_factors += 1
        if abs(metrics.get('daily_change_pct', 0)) > 5:
            risk_factors += 1
        if metrics.get('max_drawdown', 0) < -15:
            risk_factors += 1
        
        if risk_factors >= 2:
            flags['risk_level'] = 'high'
        elif risk_factors == 1:
            flags['risk_level'] = 'medium'
        
        return flags

# Example usage
if __name__ == "__main__":
    # This would typically be used with real data
    print("Market Metrics Calculator module loaded successfully")
    print("Use with EquityDataProvider and SignalGenerator for comprehensive analysis")
