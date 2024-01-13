import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
import smtplib
from email.message import EmailMessage

import indicators

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

# Function to check if there's a new signal
def is_new_signal(signal_date, file_path='last_signal_date.csv'):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        # File doesn't exist or is empty
        return True
    else:
        df = pd.read_csv(file_path)
        if 'date' not in df.columns:
            return True
        last_dates = df['date']
        return signal_date not in last_dates.values

# Function to update the date in the file
def update_last_signal_date(signal_date, file_path='last_signal_date.csv'):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        df = pd.DataFrame(columns=['date'])
    else:
        df = pd.read_csv(file_path)
    
    new_row = {'date': signal_date}
    df = df._append(new_row, ignore_index=True)
    df.to_csv(file_path, index=False)
    
def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "franciscoboudagh1@gmail.com"
    msg['from'] = user
    password = "utwzrzqzadlphhxm"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

# Function to plot indicators
def plot_with_indicator(df, indicator, ticker_symbol):
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], close_prices, label='Close Price', alpha=0.6)

    start_date = df['Date'].iloc[0].strftime('%Y-%m-%d')
    end_date = df['Date'].iloc[-1].strftime('%Y-%m-%d')
    title_suffix = f" ({start_date} to {end_date})"
    
    if indicator == 'RSI':
        buy_signals, sell_signals = indicators.rsi_signals(close_prices)

    elif indicator == 'MACD':
        buy_signals, sell_signals = indicators.macd_signals(close_prices)

    elif indicator == 'Stochastic':
        buy_signals, sell_signals = indicators.stochastic_signals(df)
    

    # Handling signals and email alerts
    latest_buy_signal = df['Date'][buy_signals].max() if buy_signals.any() else None
    latest_sell_signal = df['Date'][sell_signals].max() if sell_signals.any() else None
    latest_signal_date = max(latest_buy_signal, latest_sell_signal)

    if latest_signal_date and is_new_signal(latest_signal_date.strftime('%Y-%m-%d')):
        signal_type = 'Buy' if latest_buy_signal == latest_signal_date else 'Sell'
        update_last_signal_date(latest_signal_date.strftime('%Y-%m-%d'))
        # Send email alert
        email_body = f"New signal: {signal_type}\nTicker: {ticker_symbol}\nDate: {latest_signal_date.strftime('%Y-%m-%d')}"
        email_alert("New Trading Signal", email_body, "franciscoboudagh1@gmail.com")


    plt.scatter(df['Date'][buy_signals], close_prices[buy_signals], color='green', label='Buy Signal', marker='^')
    plt.scatter(df['Date'][sell_signals], close_prices[sell_signals], color='red', label='Sell Signal', marker='v')
    plt.title(f'{ticker_symbol} with {indicator} Indicator. Buy/Sell Signals{title_suffix}')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

    
    
# Main execution
if __name__ == "__main__":
    # Fetch data from yfinance using configuration
    ticker_symbol = config['ticker_symbol']
    start_date = config['start_date']
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(start=start_date)
    df.reset_index(inplace=True)
    close_prices = df['Close']

    # Indicator choice from configuration
    indicator_choice = config['indicator_choice']
    plot_with_indicator(df, indicator=indicator_choice, ticker_symbol=ticker_symbol)