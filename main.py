import tkinter as tk
import requests
import json
import pandas as pd
from transformers import pipeline
from tkinter import ttk
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


# Initialize sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

def fetch_news(stock_symbol):
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = json.loads(response.text)
    
    if 'articles' in data:
        headlines = [article['title'] for article in data['articles'][:5]]
        return headlines
    else:
        print(f"Error fetching news: {data}")
        return ["Error fetching news"]
    
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data.ewm(span=short_window, adjust=False).mean()
    long_ema = data.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return round(macd.iloc[-1], 4), round(signal_line.iloc[-1], 4)

def calculate_bollinger_bands(data, window=20):
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    return round(upper_band.iloc[-1], 4), round(lower_band.iloc[-1], 4)

def calculate_rsi(data, window):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 4)

def calculate_ema(data, window):
    return round(data.ewm(span=window, adjust=False).mean().iloc[-1], 4)

def analyze_sentiment(stock_data, news_headlines, rsi_window=14, ema_window=9):
    df = pd.DataFrame(stock_data).T.astype(float)
    close_prices = df["4. close"]
    
    moving_average = round(close_prices.mean(), 4)
    avg_volume = round(df["5. volume"].mean(), 4)
    rsi = calculate_rsi(close_prices, rsi_window)
    ema = calculate_ema(close_prices, ema_window)
    
    macd, signal_line = calculate_macd(close_prices)
    upper_band, lower_band = calculate_bollinger_bands(close_prices)
    news_sentiment = sentiment_analyzer(news_headlines)
    avg_sentiment = round(sum([s['score'] for s in news_sentiment]) / len(news_sentiment), 4)
    
    sentiment = "Undecided"
    confidence = 0.5
    
        # Initialize scoring system
    score = 0
    
    # Scoring based on moving average
    if moving_average > 100:
        score += 1
    elif moving_average < 50:
        score -= 1
    
    # Scoring based on volume
    if avg_volume > 1000:
        score += 1
    elif avg_volume < 1000:
        score -= 1
    
    # Scoring based on news sentiment
    if avg_sentiment > 0.6:
        score += 1
    elif avg_sentiment < 0.4:
        score -= 1
    
    # Scoring based on RSI
    if rsi < 70:
        score += 1
    elif rsi > 70:
        score -= 1
    
    # Scoring based on EMA
    if ema > moving_average:
        score += 1
    elif ema < moving_average:
        score -= 1
    
    # Scoring based on MACD and Signal Line
    if macd > signal_line:
        score += 1
    elif macd < signal_line:
        score -= 1
    
    # Scoring based on Bollinger Bands
    if close_prices.iloc[-1] > upper_band:
        score -= 1
    elif close_prices.iloc[-1] < lower_band:
        score += 1
    
    # Determine sentiment and confidence based on score
    if score > 0:
        sentiment = "Buy"
        confidence = min(0.5 + (score * 0.1), 1)
    elif score < 0:
        sentiment = "Sell"
        confidence = min(0.5 + (abs(score) * 0.1), 1)
    else:
        sentiment = "Undecided"
        confidence = 0.5
    
    return sentiment, confidence, moving_average, avg_volume, avg_sentiment, rsi, ema, macd, signal_line, upper_band, lower_band


def fetch_stock_data():
    stock_symbol = stock_entry.get()
    print(f"Fetching data for {stock_symbol}")
    
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval=5min&apikey={API_KEY}"
    response = requests.get(url)
    data = json.loads(response.text)
    
    news_headlines = fetch_news(stock_symbol)

    # Get user-defined window sizes from dropdowns
    rsi_window = int(rsi_window_var.get())
    ema_window = int(ema_window_var.get())
    
    if "Time Series (5min)" in data:
        # Modify the analyze_sentiment function call to pass these window sizes
        sentiment, confidence, moving_average, avg_volume, avg_sentiment, rsi, ema, macd, signal_line, upper_band, lower_band = analyze_sentiment(data["Time Series (5min)"], news_headlines, rsi_window, ema_window)
        
        # Update the confidence score to be an actual percentage
        confidence_percentage = round(confidence * 100, 2)
        
        stock_label.config(text=f"Sentiment: {sentiment}\nConfidence: {confidence_percentage}%\nMoving Average: {moving_average}\nAverage Volume: {avg_volume}\nNews Sentiment: {avg_sentiment}\nRSI: {rsi}\nEMA: {ema}\nMACD: {macd}\nSignal Line: {signal_line}\nUpper Band: {upper_band}\nLower Band: {lower_band}")
    else:
        stock_label.config(text="Invalid Stock Symbol or API Error")

    
    

# Initialize the Tkinter window
root = tk.Tk()
root.title("Stock Analysis App")
root.geometry("600x600")

# Add a label to the window
label = tk.Label(root, text="Welcome to the Stock Analysis App", font=("Arial", 16), fg="blue")
label.pack(pady=10)

# Add an entry widget to input stock symbol
stock_entry = ttk.Entry(root, width=30, font=("Arial", 14))
stock_entry.pack(pady=10)
stock_entry.insert(0, "Enter Stock Symbol")

# Add labels and dropdowns for indicator windows
rsi_label = tk.Label(root, text="Select RSI Window:", font=("Arial", 14))
rsi_label.pack(pady=5)
rsi_window_values = [str(i) for i in [7, 14, 21, 28]]
rsi_window_var = tk.StringVar()
rsi_window_var.set("14")  # default value
rsi_window_dropdown = ttk.Combobox(root, textvariable=rsi_window_var, values=rsi_window_values)
rsi_window_dropdown.pack(pady=5)

ema_label = tk.Label(root, text="Select EMA Window:", font=("Arial", 14))
ema_label.pack(pady=5)
ema_window_values = [str(i) for i in [7, 9, 12, 26]]
ema_window_var = tk.StringVar()
ema_window_var.set("9")  # default value
ema_window_dropdown = ttk.Combobox(root, textvariable=ema_window_var, values=ema_window_values)
ema_window_dropdown.pack(pady=5)

# Add a button to fetch stock data
fetch_button = ttk.Button(root, text="Fetch Data", command=fetch_stock_data)
fetch_button.pack(pady=10)

# Add a label to display stock data
stock_label = tk.Label(root, text="", font=("Arial", 12), fg="green")
stock_label.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
