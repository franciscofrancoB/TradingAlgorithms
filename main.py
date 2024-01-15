import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
import smtplib
from email.message import EmailMessage
import indicators
import json

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
    password = "xxxxxxxxxxxxxxx"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()





def simulate_portfolio(df, buy_signals, sell_signals, initial_shares=config['initial_shares']):
    cash = 0
    shares = initial_shares
    share_price_initial = df['Close'].iloc[0]
    cash += shares * share_price_initial
    portfolio_values = []

    for i in range(len(df)):
        if buy_signals[i] and cash >= df['Close'][i]:
            shares += 1
            cash -= df['Close'][i]
        elif sell_signals[i] and shares > 0:
            shares -= 1
            cash += df['Close'][i]
        portfolio_value = cash + shares * df['Close'][i]
        portfolio_values.append(portfolio_value)

    return portfolio_values

def plot_portfolio_value(df, portfolio_values, indicator, ticker_symbol):
    plt.figure(figsize=(10, 6))

    # Absolute portfolio value
    ax1 = plt.gca()
    ax1.plot(df['Date'], portfolio_values)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Portfolio Value')
    ax1.tick_params(axis='y')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45)

    # Percentage growth on a secondary axis
    initial_value = portfolio_values[0]
    percentage_growth = [(value - initial_value) / initial_value * 100 for value in portfolio_values]
    ax2 = ax1.twinx()
    ax2.plot(df['Date'], percentage_growth)
    ax2.set_ylabel('Percentage Growth (%)')
    ax2.tick_params(axis='y')
    start_date = df['Date'].iloc[0].strftime('%Y-%m-%d')
    end_date = df['Date'].iloc[-1].strftime('%Y-%m-%d')
    plt.title(f'Portfolio Value Growth | {ticker_symbol} using {indicator} ({start_date} to {end_date})')
    
    plt.axhline(y=0, color="grey")
    plt.tight_layout()
    plt.show()







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

    return buy_signals, sell_signals

    
# Main execution
if __name__ == "__main__":
    # Fetch data from yfinance
    ticker_symbol = config['ticker_symbol']
    start_date = config['start_date']
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(start=start_date)
    df.reset_index(inplace=True)
    close_prices = df['Close']

    # Indicator choice
    indicator_choice = config['indicator_choice']

    buy_signals, sell_signals = plot_with_indicator(df, indicator=indicator_choice, ticker_symbol=ticker_symbol)
    portfolio_values = simulate_portfolio(df, buy_signals, sell_signals)
    plot_portfolio_value(df, portfolio_values, indicator=indicator_choice, ticker_symbol=ticker_symbol)