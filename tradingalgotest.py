import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf

# RSI Calculation function
def calculate_rsi(data, window=14):
    delta = data.diff()
    up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
    ema_up = up.ewm(span=window, adjust=False).mean()
    ema_down = down.ewm(span=window, adjust=False).mean()
    rs = ema_up / ema_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

# MACD Calculation Function
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data.ewm(span=short_window, adjust=False).mean()
    long_ema = data.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    return macd_line, signal_line


""" # OPTION 1: Read CSV file
df = pd.read_csv('AAPL.csv')
df['Date'] = pd.to_datetime(df['Date'])
close_prices = df['Close'] """

# OPTION 2: Fetch data from yfinance
ticker_symbol = "AAPL"
ticker = yf.Ticker(ticker_symbol)
df = ticker.history(start="2022-01-01")
df.reset_index(inplace=True)
close_prices = df['Close']


# Function to plot indicators
def plot_with_indicator(df, indicator, ticker_symbol):
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], close_prices, label='Close Price', alpha=0.6)

    start_date = df['Date'].iloc[0].strftime('%Y-%m-%d')
    end_date = df['Date'].iloc[-1].strftime('%Y-%m-%d')
    title_suffix = f" ({start_date} to {end_date})"
    
    if indicator == 'RSI':
        rsi = calculate_rsi(close_prices)
        buy_signals = rsi < 30
        sell_signals = rsi > 70
        plt.scatter(df['Date'][buy_signals], close_prices[buy_signals], color='green', label='Buy Signal', marker='^')
        plt.scatter(df['Date'][sell_signals], close_prices[sell_signals], color='red', label='Sell Signal', marker='v')

    elif indicator == 'MACD':
        macd_line, signal_line = calculate_macd(close_prices)
        buy_signals = (macd_line > signal_line) & (macd_line.shift() <= signal_line.shift())
        sell_signals = (macd_line < signal_line) & (macd_line.shift() >= signal_line.shift())
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


# Choose indicator and plot
# Options: 'RSI', 'MACD'
indicator_choice = 'RSI'
plot_with_indicator(df, indicator=indicator_choice, ticker_symbol=ticker_symbol)