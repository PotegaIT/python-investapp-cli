### 🇺🇸 English Version:

# InvestApp CLI - Automated ETF Portfolio Rebalancing   

**InvestApp CLI** is a terminal-based investment tool written in Python, designed to replace cumbersome Excel spreadsheets for passive investors. The application automates the process of portfolio rebalancing, technical analysis, and diversification tracking by connecting directly to financial APIs.   

### 🚀 Key Features
* **Intelligent Rebalancing:** Automatically calculates the exact number of units to buy based on your target allocation and current deposit, accounting for EUR/USD exchange rates.
* **Real-time Data:** Fetches live ETF prices and currency rates using the `yfinance` API.
* **Correlation Matrix:** Detects "fake diversification" by analyzing historical data (6 months) to show how closely your assets move together.
* **Technical Analysis:**   
  *  **Emotional Brake:** Uses RSI indicators to warn when the market is "Overheated" or presents a "Bargain".
  *  **Trend Tracking:** Monitors SMA 50 and SMA 200 to identify long-term growth trends.
* **Visualizations:** Generates professional dual-panel charts with Price/SMA50 and MACD indicators using Matplotlib.
* **Data Management:** A dedicated CRUD module for managing your ETF database stored in a local CSV file.

### 🛠 Tech Stack
* **Python 3.x**
* **Pandas:** Data manipulation and mathematical calculations.
* **yfinance:** Real-time market data API.
* **StockStats & TA:** Technical analysis engines.
* **Matplotlib:** Data visualization.
* **Tabulate:** Professional CLI table formatting

### 📁 Project Structure
* `main.py`: The "Conductor" – handles the CLI menu and user interaction.
* `analyze.py`: The "Brain" – contains rebalancing logic, correlation algorithms, and technical indicators.
* `etf_db.py`: The "Data Layer" – manages the CSV database initialization and updates.
* `chart/app.py`: The "Visualizer" – handles Matplotlib chart generation.
* `my_etf.csv`: Local storage for your portfolio tickers, units, and target weights.

### ⚙️ Installation
1. Clone the repository.
2. Install dependencies.
3. Run the application.


