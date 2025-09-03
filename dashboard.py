"""
Streamlit Dashboard for Equity Market Signal Analyzer
Interactive web interface for equity analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from equity_data import EquityDataProvider
from signal_generator import SignalGenerator
from market_metrics import MarketMetricsCalculator

# Page configuration
st.set_page_config(
    page_title="Equity Signal Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .signal-buy {
        color: #28a745;
        font-weight: bold;
    }
    .signal-sell {
        color: #dc3545;
        font-weight: bold;
    }
    .signal-hold {
        color: #ffc107;
        font-weight: bold;
    }
    .attention-flag {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitDashboard:
    """Streamlit dashboard for equity analysis"""
    
    def __init__(self):
        self.data_provider = EquityDataProvider()
        self.signal_generator = SignalGenerator()
        self.metrics_calculator = MarketMetricsCalculator()
    
    def run(self):
        """Main dashboard interface"""
        # Header
        st.markdown('<h1 class="main-header">📈 Equity Signal Analyzer</h1>', unsafe_allow_html=True)
        st.markdown("Professional equity market analysis and signal generation")
        
        # GitHub link
        st.markdown("""
        <div style="text-align: center; margin: 10px 0;">
            <a href="https://github.com/dev7878/equity-signal-analyzer" target="_blank" style="text-decoration: none;">
                <span style="background-color: #24292e; color: white; padding: 8px 16px; border-radius: 6px; font-size: 14px; font-weight: 500;">
                    🔗 View Source Code on GitHub
                </span>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        self._create_sidebar()
        
        # Main content
        if st.session_state.get('analyze_clicked', False):
            self._display_analysis()
        else:
            self._display_welcome()
    
    def _create_sidebar(self):
        """Create sidebar controls"""
        st.sidebar.header("🔧 Analysis Parameters")
        
        # Ticker selection
        st.sidebar.subheader("Stock Selection")
        ticker = st.sidebar.selectbox(
            "Select TSX Ticker",
            options=list(self.data_provider.supported_tickers.keys()),
            index=0
        )
        
        # Custom ticker input
        custom_ticker = st.sidebar.text_input("Or enter custom ticker (e.g., AAPL, MSFT)")
        if custom_ticker:
            ticker = custom_ticker.upper()
        
        # Date range
        st.sidebar.subheader("Date Range")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now()
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                max_value=datetime.now()
            )
        
        # Analysis options
        st.sidebar.subheader("Analysis Options")
        include_benchmark = st.sidebar.checkbox("Include TSX Benchmark Comparison", value=True)
        show_advanced_metrics = st.sidebar.checkbox("Show Advanced Metrics", value=False)
        
        # Analyze button
        if st.sidebar.button("🚀 Analyze Equity", type="primary"):
            st.session_state['analyze_clicked'] = True
            st.session_state['ticker'] = ticker
            st.session_state['start_date'] = start_date.strftime('%Y-%m-%d')
            st.session_state['end_date'] = end_date.strftime('%Y-%m-%d')
            st.session_state['include_benchmark'] = include_benchmark
            st.session_state['show_advanced_metrics'] = show_advanced_metrics
        
        # GitHub link in sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <div style="text-align: center;">
            <a href="https://github.com/dev7878/equity-signal-analyzer" target="_blank" style="text-decoration: none;">
                <span style="background-color: #24292e; color: white; padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: 500;">
                    🔗 GitHub
                </span>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    def _display_welcome(self):
        """Display welcome screen"""
        st.markdown("""
        ## Welcome to the Equity Signal Analyzer
        
        This professional-grade equity analysis tool provides comprehensive market insights for global equity markets.
        
        ### Features:
        - **Advanced Signal Generation**: RSI, MACD, Bollinger Bands, Moving Averages
        - **Volatility Analysis**: Regime classification and cluster detection
        - **Liquidity Metrics**: Volume analysis and market quality indicators
        - **Relative Performance**: Benchmark comparison and sector analysis
        - **Risk Assessment**: VaR, drawdown, and attention flagging
        
        ### Supported TSX Tickers:
        """)
        
        # Display supported tickers in a nice grid
        tickers_df = pd.DataFrame([
            {'Ticker': ticker, 'Company': name}
            for ticker, name in self.data_provider.supported_tickers.items()
        ])
        
        st.dataframe(tickers_df, use_container_width=True)
        
        st.markdown("""
        ### Getting Started:
        1. Select a ticker from the sidebar
        2. Choose your analysis date range
        3. Click "Analyze Equity" to begin
        
        The analysis will generate comprehensive signals, metrics, and visualizations.
        """)
    
    def _display_analysis(self):
        """Display analysis results"""
        ticker = st.session_state['ticker']
        start_date = st.session_state['start_date']
        end_date = st.session_state['end_date']
        include_benchmark = st.session_state['include_benchmark']
        show_advanced_metrics = st.session_state['show_advanced_metrics']
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Fetch data
            status_text.text("Fetching equity data...")
            progress_bar.progress(20)
            
            equity_data = self.data_provider.fetch_equity_data(ticker, start_date, end_date)
            
            # Fetch benchmark if requested
            benchmark_data = None
            if include_benchmark:
                status_text.text("Fetching benchmark data...")
                progress_bar.progress(40)
                benchmark_data = self.data_provider.fetch_benchmark_data(start_date, end_date)
            
            # Generate signals
            status_text.text("Generating trading signals...")
            progress_bar.progress(60)
            
            equity_data_with_signals = self.signal_generator.generate_signals(equity_data)
            
            # Calculate metrics
            status_text.text("Calculating market metrics...")
            progress_bar.progress(80)
            
            market_metrics = self.metrics_calculator.calculate_all_metrics(
                equity_data_with_signals, benchmark_data
            )
            
            # Calculate relative performance
            relative_performance = None
            if benchmark_data is not None:
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
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            self._display_overview(equity_data_with_signals, market_metrics, attention_flags, signal_accuracy)
            self._display_price_chart(equity_data_with_signals, benchmark_data)
            self._display_technical_indicators(equity_data_with_signals)
            self._display_volatility_analysis(equity_data_with_signals)
            self._display_metrics(market_metrics, show_advanced_metrics)
            
            if relative_performance is not None:
                self._display_relative_performance(relative_performance)
            
            # Download options
            self._display_download_options(equity_data_with_signals, market_metrics, attention_flags)
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.session_state['analyze_clicked'] = False
    
    def _display_overview(self, data, metrics, flags, accuracy):
        """Display overview metrics"""
        st.header("📊 Analysis Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            signal_map = {-1: "SELL", 0: "HOLD", 1: "BUY"}
            latest_signal = data['Composite_Signal'].iloc[-1]
            signal_class = "signal-sell" if latest_signal == -1 else "signal-buy" if latest_signal == 1 else "signal-hold"
            st.markdown("**Latest Signal**")
            st.markdown(f'<div class="metric-value {signal_class}">{signal_map[latest_signal]}</div>', unsafe_allow_html=True)
        
        with col2:
            st.metric("Current Price", f"${metrics['current_price']:.2f}")
        
        with col3:
            st.metric("Daily Change", f"{metrics['daily_change_pct']:.2f}%")
        
        with col4:
            st.metric("Signal Accuracy", f"{accuracy:.1f}%")
        
        # Attention flags
        if flags['requires_attention']:
            st.markdown('<div class="attention-flag">', unsafe_allow_html=True)
            st.warning(f"⚠️ **Requires Attention** - Risk Level: {flags['risk_level'].upper()}")
            if flags['attention_reasons']:
                st.write("**Reasons:**")
                for reason in flags['attention_reasons']:
                    st.write(f"• {reason}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    def _display_price_chart(self, data, benchmark_data):
        """Display price chart with signals"""
        st.header("📈 Price Chart & Signals")
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Price & Signals', 'Volume'),
            row_heights=[0.7, 0.3]
        )
        
        # Price candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['BB_Upper'],
                line=dict(color='rgba(128,128,128,0.5)'),
                name='BB Upper',
                showlegend=False
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['BB_Lower'],
                line=dict(color='rgba(128,128,128,0.5)'),
                name='BB Lower',
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Moving averages
        for ma in ['MA_20', 'MA_50']:
            if ma in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data[ma],
                        line=dict(width=1),
                        name=ma.replace('MA_', 'MA '),
                        showlegend=True
                    ),
                    row=1, col=1
                )
        
        # Buy/Sell signals
        buy_signals = data[data['Composite_Signal'] == 1]
        sell_signals = data[data['Composite_Signal'] == -1]
        
        if not buy_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals['Close'],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color='green'),
                    name='Buy Signal'
                ),
                row=1, col=1
            )
        
        if not sell_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index,
                    y=sell_signals['Close'],
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=10, color='red'),
                    name='Sell Signal'
                ),
                row=1, col=1
            )
        
        # Volume
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color='lightblue',
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Benchmark if available
        if benchmark_data is not None:
            # Normalize benchmark to start at same level as equity
            benchmark_normalized = benchmark_data['Close'] / benchmark_data['Close'].iloc[0] * data['Close'].iloc[0]
            fig.add_trace(
                go.Scatter(
                    x=benchmark_data.index,
                    y=benchmark_normalized,
                    line=dict(color='orange', dash='dash'),
                    name='TSX Benchmark'
                ),
                row=1, col=1
            )
        
        fig.update_layout(
            title=f"Price Analysis - {st.session_state['ticker']}",
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_technical_indicators(self, data):
        """Display technical indicators"""
        st.header("🔧 Technical Indicators")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # RSI
            fig_rsi = go.Figure()
            fig_rsi.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['RSI'],
                    line=dict(color='purple'),
                    name='RSI'
                )
            )
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
            fig_rsi.update_layout(title="RSI (14)", height=300)
            st.plotly_chart(fig_rsi, use_container_width=True)
        
        with col2:
            # MACD
            fig_macd = go.Figure()
            fig_macd.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['MACD'],
                    line=dict(color='blue'),
                    name='MACD'
                )
            )
            fig_macd.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['MACD_Signal'],
                    line=dict(color='red'),
                    name='Signal'
                )
            )
            fig_macd.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['MACD_Histogram'],
                    name='Histogram',
                    marker_color='gray',
                    opacity=0.7
                )
            )
            fig_macd.update_layout(title="MACD", height=300)
            st.plotly_chart(fig_macd, use_container_width=True)
    
    def _display_volatility_analysis(self, data):
        """Display volatility analysis"""
        st.header("📊 Volatility Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Volatility over time
            fig_vol = go.Figure()
            fig_vol.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Volatility'] * 100,
                    line=dict(color='orange'),
                    name='20-Day Volatility'
                )
            )
            fig_vol.update_layout(
                title="Volatility Over Time",
                yaxis_title="Volatility (%)",
                height=300
            )
            st.plotly_chart(fig_vol, use_container_width=True)
        
        with col2:
            # Volatility regime
            regime_colors = {0: 'green', 1: 'yellow', 2: 'red'}
            regime_names = {0: 'Low', 1: 'Medium', 2: 'High'}
            
            fig_regime = go.Figure()
            for regime in [0, 1, 2]:
                regime_data = data[data['Volatility_Regime'] == regime]
                if not regime_data.empty:
                    fig_regime.add_trace(
                        go.Scatter(
                            x=regime_data.index,
                            y=regime_data['Volatility'] * 100,
                            mode='markers',
                            marker=dict(color=regime_colors[regime], size=6),
                            name=f'{regime_names[regime]} Volatility'
                        )
                    )
            
            fig_regime.update_layout(
                title="Volatility Regime Classification",
                yaxis_title="Volatility (%)",
                height=300
            )
            st.plotly_chart(fig_regime, use_container_width=True)
    
    def _display_metrics(self, metrics, show_advanced):
        """Display market metrics"""
        st.header("📋 Market Metrics")
        
        # Basic metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Volatility (20d)", f"{metrics.get('volatility_20d', 0):.2f}%")
            st.metric("Daily Spread", f"{metrics.get('daily_spread_pct', 0):.2f}%")
        
        with col2:
            st.metric("Volume Ratio", f"{metrics.get('volume_ratio', 0):.2f}")
            st.metric("Liquidity Score", f"{metrics.get('liquidity_score', 0):.0f}")
        
        with col3:
            st.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}")
            st.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0):.2f}%")
        
        with col4:
            st.metric("VaR (5%)", f"{metrics.get('var_5pct', 0):.2f}%")
            st.metric("Beta", f"{metrics.get('beta', 0):.2f}")
        
        # Advanced metrics
        if show_advanced:
            st.subheader("Advanced Metrics")
            
            advanced_metrics = {
                'Expected Shortfall (5%)': metrics.get('expected_shortfall_5pct', 0),
                'Sortino Ratio': metrics.get('sortino_ratio', 0),
                'Information Ratio': metrics.get('information_ratio', 0),
                'Alpha': metrics.get('alpha', 0),
                'Price Efficiency': metrics.get('price_efficiency', 0),
                'Market Impact Proxy': metrics.get('market_impact_proxy', 0)
            }
            
            for metric, value in advanced_metrics.items():
                if isinstance(value, (int, float)) and not np.isnan(value) and not np.isinf(value):
                    st.metric(metric, f"{value:.4f}")
    
    def _display_relative_performance(self, relative_perf):
        """Display relative performance vs benchmark"""
        st.header("📊 Relative Performance vs TSX Benchmark")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cumulative relative performance
            fig_rel = go.Figure()
            fig_rel.add_trace(
                go.Scatter(
                    x=relative_perf.index,
                    y=relative_perf['Cumulative_Relative_Perf'] * 100,
                    line=dict(color='blue'),
                    name='Cumulative Relative Performance'
                )
            )
            fig_rel.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_rel.update_layout(
                title="Cumulative Relative Performance",
                yaxis_title="Relative Performance (%)",
                height=300
            )
            st.plotly_chart(fig_rel, use_container_width=True)
        
        with col2:
            # Rolling correlation
            fig_corr = go.Figure()
            fig_corr.add_trace(
                go.Scatter(
                    x=relative_perf.index,
                    y=relative_perf['Rolling_Correlation'],
                    line=dict(color='green'),
                    name='Rolling Correlation'
                )
            )
            fig_corr.update_layout(
                title="Rolling Correlation with Benchmark",
                yaxis_title="Correlation",
                height=300
            )
            st.plotly_chart(fig_corr, use_container_width=True)
    
    def _display_download_options(self, data, metrics, flags):
        """Display download options"""
        st.header("💾 Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download CSV
            csv_data = data.to_csv()
            st.download_button(
                label="📊 Download Data (CSV)",
                data=csv_data,
                file_name=f"{st.session_state['ticker']}_data.csv",
                mime="text/csv"
            )
        
        with col2:
            # Download JSON
            json_data = {
                'ticker': st.session_state['ticker'],
                'analysis_date': datetime.now().isoformat(),
                'metrics': metrics,
                'attention_flags': flags
            }
            st.download_button(
                label="📋 Download Metrics (JSON)",
                data=json.dumps(json_data, indent=2, default=str),
                file_name=f"{st.session_state['ticker']}_metrics.json",
                mime="application/json"
            )
        
        with col3:
            # Reset analysis
            if st.button("🔄 New Analysis"):
                st.session_state['analyze_clicked'] = False
                st.rerun()

def main():
    """Main function to run the dashboard"""
    dashboard = StreamlitDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
