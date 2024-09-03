import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt

# List of stock tickers (example subset)
tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "NFLX", "FB", "NVDA", "BABA", "V"]

def fetch_stock_data(ticker, period="1mo"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def calculate_indicators(df):
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_Signal'] = macd['MACDs_12_26_9']
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    return df

def buy_signal(row):
    return (row['MACD'] > row['MACD_Signal']) and (row['Close'] > row['VWAP'])

def sell_signal(row, bought_price):
    return (row['MACD'] < row['MACD_Signal']) or ((row['Close'] / bought_price) >= 1.02) or ((row['Close'] / bought_price) <= 0.99)

def analyze_stock(ticker):
    df = fetch_stock_data(ticker)
    df = calculate_indicators(df)
    return df

def simulate_trading(tickers, initial_balance):
    balance = initial_balance
    portfolio = {}
    trade_log = []

    for ticker in tickers:
        df = analyze_stock(ticker)
        bought_price = 0

        for index, row in df.iterrows():
            if ticker not in portfolio and buy_signal(row):
                shares_to_buy = balance / row['Close']
                portfolio[ticker] = shares_to_buy
                bought_price = row['Close']
                balance = 0  # Update balance after buying
                trade_log.append((row.name, ticker, 'BUY', row['Close'], balance))

            elif ticker in portfolio and sell_signal(row, bought_price):
                balance = portfolio[ticker] * row['Close']  # Calculate the balance
                del portfolio[ticker]
                trade_log.append((row.name, ticker, 'SELL', row['Close'], balance))

    # Final balance calculation after last day prices
    for ticker in portfolio:
        df = analyze_stock(ticker)
        balance += portfolio[ticker] * df.iloc[-1]['Close']
        trade_log.append((df.index[-1], ticker, 'SELL', df.iloc[-1]['Close'], balance))

    return balance, trade_log

def visualize_trading(trade_log, ticker):
    df = analyze_stock(ticker)
    plt.figure(figsize=(12, 6))
    plt.plot(df['Close'], label='Close Price')
    buy_signals = [trade[3] for trade in trade_log if trade[1] == ticker and trade[2] == 'BUY']
    sell_signals = [trade[3] for trade in trade_log if trade[1] == ticker and trade[2] == 'SELL']

    # Plot buy signals
    for i, buy_signal in enumerate(buy_signals):
        # Assuming 'Date' is your date column
        date = df.index[i]
        plt.scatter(date, buy_signal, marker='^', color='green', label='Buy Signal' if i == 0 else None)

    # Plot sell signals
    for i, sell_signal in enumerate(sell_signals):
        # Assuming 'Date' is your date column
        date = df.index[i]
        plt.scatter(date, sell_signal, marker='v', color='red', label='Sell Signal' if i == 0 else None)

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'Trading Strategy for {ticker}')
    plt.legend()
    plt.show()

# Simulate trading with an initial balance of 10000 INR
initial_balance = 10000
final_balance, trades = simulate_trading(tickers, initial_balance)

print(f"Final Balance: {final_balance:.2f} INR")
for trade in trades:
    print(trade)

visualize_trading(trades, 'AAPL')
