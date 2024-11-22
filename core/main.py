import pandas as pd
import numpy as np
import yfinance as yf
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# List of Nifty 50 stocks and their lot sizes
nifty_50_stocks = [
    "ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS",
    "BAJAJFINSV.NS", "BHARTIARTL.NS", "BPCL.NS", "BRITANNIA.NS", "CIPLA.NS",
    "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS",
    "HCLTECH.NS", "HDFC.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS",
    "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS", "INFY.NS",
    "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS",
    "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS",
    "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TATACONSUM.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"
]

lot_sizes_const = [
    1250, 300, 1200, 250, 125, 125, 1851, 1800, 200, 650,
    3200, 200, 250, 350, 950, 600, 300, 500, 1050, 300,
    1075, 300, 700, 900, 300, 950, 1350, 600, 375, 475,
    100, 50, 4000, 3850, 1550, 250, 350, 1500, 800, 500,
    2000, 425, 150, 850, 375, 125, 1300, 300
]

# Function to download 15-minute data from Yahoo Finance
def load_data_from_yahoo(stock, start_date, end_date):
    try:
        data = yf.download(tickers=stock, start=start_date, end=end_date, interval='15m')
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        print(f"Error loading data for {stock}: {e}")
        return pd.DataFrame()

# Function to preprocess data for sell transactions only
def preprocess_data_sell_only(data):
    data['Returns'] = data['Close'].pct_change()
    data['High_Low'] = (data['High'] - data['Low']) / data['Close']
    data['Open_Close'] = (data['Open'] - data['Close']) / data['Close']
    # Target: 1 if price goes down in the next interval (sell signal), 0 otherwise
    data['Target'] = (data['Close'].shift(-1) < data['Close']).astype(int)
    data.dropna(inplace=True)
    return data

# Main function to create the strategy for sell transactions
def create_trading_strategy_sell_only(training_period, testing_period,stocks = None, lot_sizes = None):
    results = []
    if stocks is None:
        stocks = nifty_50_stocks
    if lot_sizes is None:
        lot_sizes = lot_sizes_const

    for stock, lot_size in zip(stocks, lot_sizes):
        print(f"Processing {stock}...")
        # Load data
        train_data = load_data_from_yahoo(stock, *training_period)
        test_data = load_data_from_yahoo(stock, *testing_period)

        if train_data.empty or test_data.empty:
            results.append([stock, 0, 0, 0])  # No trades if data is missing
            continue

        # Preprocess data for sell transactions
        train_data = preprocess_data_sell_only(train_data)
        test_data = preprocess_data_sell_only(test_data)

        # Features and target
        X_train, y_train = train_data.drop(['Datetime', 'Target'], axis=1), train_data['Target']
        X_test, y_test = test_data.drop(['Datetime', 'Target'], axis=1), test_data['Target']

        # Model training
        model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        model.fit(X_train, y_train)

        # Predict and evaluate
        test_data['Predictions'] = model.predict(X_test)
        test_data['Probabilities'] = model.predict_proba(X_test)[:, 1]

        # Filter high-probability sell trades
        high_prob_trades = test_data[(test_data['Predictions'] == 1) & (test_data['Probabilities'] > 0.95)]
        total_trades = len(high_prob_trades)
        winning_trades = high_prob_trades[high_prob_trades['Target'] == 1].shape[0]
        profit_loss = (
            (high_prob_trades['Close'] - high_prob_trades['Close'].shift(-1)) * lot_size
        ).sum()  # Profit/Loss scaled by lot size

        # Store results
        results.append([stock, total_trades, winning_trades, profit_loss])

    # Create results dataframe
    results_df = pd.DataFrame(results, columns=['Stock', '# of Trades', '# of Winning Trades', 'Total Profit/Loss'])

    # Export to Excel
    #results_df.to_excel('trading_strategy_results_sell_only.xlsx', index=False)
    return results_df

# Parameters
#training_period = ('2024-10-01', '2024-10-30')
#testing_period = ('2024-10-31', '2024-11-15')

# Run the strategy for Nifty 50 with sell-only focus
#results_table = create_trading_strategy_sell_only(training_period, testing_period)
#print(results_table)

