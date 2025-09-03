# 📈 Equity Market Signal Analyzer

A professional-grade equity market analysis tool designed for global equity markets including TSX, NYSE, and NASDAQ. This application provides comprehensive signal generation, volatility analysis, and market quality metrics suitable for quantitative analysts and institutional traders.

## 🌐 **Live Application**

**🚀 [Try the Equity Signal Analyzer Now](https://equity-signal-analyzer-bye2ixgkh8snlduwp9utrb.streamlit.app/)**

*Analyze any equity ticker with professional-grade technical analysis and market metrics*

## 🎯 Overview

The Equity Signal Analyzer transforms raw market data into actionable insights through advanced technical analysis, volatility regime classification, and liquidity assessment. Built with institutional-grade analytics, it provides the tools used by quantitative analysts at major financial institutions.

### Key Features

- **Advanced Signal Generation**: RSI, MACD, Bollinger Bands, Moving Averages, Stochastic Oscillator
- **Volatility Analysis**: Regime classification (low/medium/high) and cluster detection
- **Market Quality Metrics**: Spread analysis, liquidity scoring, and market impact assessment
- **Relative Performance**: Benchmark comparison against market indices
- **Risk Assessment**: VaR, Expected Shortfall, Sharpe/Sortino ratios, and drawdown analysis
- **Interactive Dashboard**: Streamlit-based web interface with real-time visualizations
- **Professional Outputs**: Structured JSON reports and exportable analytics

## 🏢 Supported Equities

The analyzer supports major companies across key sectors including TSX, NYSE, and NASDAQ:

| Ticker  | Company                   | Sector             |
| ------- | ------------------------- | ------------------ |
| SHOP.TO | Shopify Inc               | Technology         |
| RY.TO   | Royal Bank of Canada      | Financial Services |
| TD.TO   | Toronto-Dominion Bank     | Financial Services |
| CNR.TO  | Canadian National Railway | Transportation     |
| CP.TO   | Canadian Pacific Railway  | Transportation     |
| AAPL    | Apple Inc                 | Technology         |
| MSFT    | Microsoft Corporation     | Technology         |
| GOOGL   | Alphabet Inc              | Technology         |

_And many more..._

## 🚀 Quick Start

### Local Development

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/equity-signal-analyzer.git
   cd equity-signal-analyzer
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**:

   ```bash
   streamlit run dashboard.py
   ```

4. **Access the application**:
   - Open your browser to `http://localhost:8501`

### Command Line Analysis

```bash
# Analyze a TSX stock
python analyze.py --ticker SHOP.TO --start 2023-01-01 --end 2023-12-31

# Analyze a US stock
python analyze.py --ticker AAPL --start 2023-01-01 --end 2023-12-31
```

## 🌐 Cloud Deployment

This application is deployed on **Streamlit Cloud** for easy access:

### Streamlit Cloud (Current)

- **Live URL**: [https://equity-signal-analyzer-bye2ixgkh8snlduwp9utrb.streamlit.app/](https://equity-signal-analyzer-bye2ixgkh8snlduwp9utrb.streamlit.app/)
- **Deployment**: Automatic from GitHub repository
- **Updates**: Automatic deployment on code changes

### Local Development

```bash
# Run locally
streamlit run dashboard.py

# Access at http://localhost:8501
```

## 📊 Usage Examples

### Web Dashboard

1. **Select a ticker**: Enter any equity symbol (e.g., SHOP.TO, AAPL)
2. **Set date range**: Choose your analysis period
3. **Click Analyze**: Generate comprehensive market analysis
4. **View results**: Interactive charts, signals, and metrics
5. **Download data**: Export JSON reports and charts

### API Integration

```python
from equity_data import EquityDataProvider
from signal_generator import SignalGenerator
from market_metrics import MarketMetricsCalculator

# Initialize components
data_provider = EquityDataProvider()
signal_generator = SignalGenerator()
metrics_calculator = MarketMetricsCalculator()

# Fetch data and generate analysis
data = data_provider.fetch_equity_data("SHOP.TO", "2023-01-01", "2023-12-31")
signals = signal_generator.generate_signals(data)
metrics = metrics_calculator.calculate_all_metrics(data)
```

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Alpha Vantage API key for enhanced data
ALPHA_VANTAGE_API_KEY=your_api_key_here

# Streamlit configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Customization

- **Add new tickers**: Edit `equity_data.py` → `supported_tickers`
- **Modify signals**: Adjust parameters in `signal_generator.py`
- **Custom metrics**: Extend `market_metrics.py`
- **UI changes**: Modify `dashboard.py`

## 📈 Sample Analysis Output

```json
{
  "metadata": {
    "ticker": "SHOP.TO",
    "analysis_date": "2023-12-31T15:30:00",
    "data_period": {
      "start_date": "2023-01-01",
      "end_date": "2023-12-31",
      "total_days": 250
    }
  },
  "signals": {
    "latest_signal": 1,
    "signal_breakdown": {
      "rsi_signal": -1,
      "macd_signal": 1,
      "bollinger_signal": 0,
      "ma_signal": 1,
      "volume_signal": 0
    },
    "directional_accuracy": 68.5
  },
  "volatility_regime": {
    "current_regime": 1,
    "regime_description": "medium",
    "volatility_cluster": false
  },
  "market_metrics": {
    "current_price": 125.67,
    "daily_change_pct": 2.34,
    "volatility_20d": 28.5,
    "liquidity_score": 85.2
  }
}
```

## 🛠️ Development

### Project Structure

```
equity-signal-analyzer/
├── dashboard.py              # Streamlit web interface
├── analyze.py                # Command-line interface
├── equity_data.py            # Data fetching and processing
├── signal_generator.py       # Technical analysis and signals
├── market_metrics.py         # Market quality metrics
├── main.py                   # Google Cloud entry point
├── app.yaml                  # Google Cloud configuration
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
└── README.md                # This file
```

### Testing

```bash
# Run test suite
python test_analyzer.py

# Test specific components
python -c "from equity_data import EquityDataProvider; print('✅ Data module OK')"
python -c "from signal_generator import SignalGenerator; print('✅ Signals module OK')"
python -c "from market_metrics import MarketMetricsCalculator; print('✅ Metrics module OK')"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and request features on GitHub Issues
- **Documentation**: Check the deployment guides and code comments
- **Community**: Join discussions in GitHub Discussions

## 🎯 Roadmap

- [ ] Real-time data streaming
- [ ] Machine learning signal enhancement
- [ ] Portfolio optimization features
- [ ] Mobile app interface
- [ ] Advanced backtesting capabilities

---

**Built for quantitative analysts and institutional traders** | **Global Market Support** | **Professional Grade Analytics**
