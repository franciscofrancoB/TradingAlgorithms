# RSI Calculation function
def calculate_rsi(data, window=14):
    delta = data.diff()
    up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
    ema_up = up.ewm(span=window, adjust=False).mean()
    ema_down = down.ewm(span=window, adjust=False).mean()
    rs = ema_up / ema_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to generate RSI signals
def rsi_signals(data, window=14):
    rsi = calculate_rsi(data, window)
    buy_signals = rsi < 30
    sell_signals = rsi > 70
    return buy_signals, sell_signals


# MACD Calculation Function
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data.ewm(span=short_window, adjust=False).mean()
    long_ema = data.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    return macd_line, signal_line

# Function to generate MACD signals
def macd_signals(data, short_window=12, long_window=26, signal_window=9):
    macd_line, signal_line = calculate_macd(data, short_window, long_window, signal_window)
    buy_signals = (macd_line > signal_line) & (macd_line.shift() <= signal_line.shift())
    sell_signals = (macd_line < signal_line) & (macd_line.shift() >= signal_line.shift())
    return buy_signals, sell_signals


# Stochastic Oscillator Calculation Function
def calculate_stochastic_oscillator(data, k_window=14, d_window=3):
    low_min = data['Low'].rolling(window=k_window).min()
    high_max = data['High'].rolling(window=k_window).max()
    K_line = ((data['Close'] - low_min) / (high_max - low_min)) * 100
    D_line = K_line.rolling(window=d_window).mean()
    return K_line, D_line

# Function to generate Stochastic signals
def stochastic_signals(data, k_window=14, d_window=3):
    K_line, D_line = calculate_stochastic_oscillator(data, k_window, d_window)
    buy_signals = (K_line > D_line) & (K_line < 20)
    sell_signals = (K_line < D_line) & (K_line > 80)
    return buy_signals, sell_signals