import tkinter as tk
import requests
import json
import pandas as pd
from transformers import pipeline
from tkinter import ttk

API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"
NEWS_API_KEY = "YOUR_NEWS_API_KEY"

# Initialize sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

def fetch_news(stock_symbol):
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = json.loads(response.text)
    headlines = [article['title'] for article in data['articles'][:5]]
    return headlines

def calculate_rsi(data, window):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 4)

def calculate_ema(data, window):
    return round(data.ewm(span=window, adjust=False).mean().iloc[-1], 4)

def analyze_sentiment(stock_data, news_headlines):
    df = pd.DataFrame(stock_data).T.astype(float)
    close_prices = df["4. close"]
    
    moving_average = round(close_prices.mean(), 4)
    avg_volume = round(df["5. volume"].mean(), 4)
    rsi = calculate_rsi(close_prices, 14)
    ema = calculate_ema(close_prices, 9)
    
    news_sentiment = sentiment_analyzer(news_headlines)
    avg_sentiment = round(sum([s['score'] for s in news_sentiment]) / len(news_sentiment), 4)
    
    sentiment = "Undecided"
    confidence = 0.5
    
    if moving_average > 100 and avg_volume > 1000 and avg_sentiment > 0.6 and rsi < 70 and ema > moving_average:
        sentiment = "Buy"
        confidence = 0.9
    elif moving_average < 50 and avg_volume < 1000 and avg_sentiment < 0.4 and rsi > 30 and ema < moving_average:
        sentiment = "Sell"
        confidence = 0.8
    
    return sentiment, confidence, moving_average, avg_volume, avg_sentiment, rsi, ema

def fetch_stock_data():
    stock_symbol = stock_entry.get()
    print(f"Fetching data for {stock_symbol}")
    
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval=5min&apikey={API_KEY}"
    response = requests.get(url)
    data = json.loads(response.text)
    
    news_headlines = fetch_news(stock_symbol)
    
    if "Time Series (5min)" in data:
        sentiment, confidence, moving_average, avg_volume, avg_sentiment, rsi, ema = analyze_sentiment(data["Time Series (5min)"], news_headlines)
        stock_label.config(text=f"Sentiment: {sentiment}\nConfidence: {confidence * 100}%\nMoving Average: {moving_average}\nAverage Volume: {avg_volume}\nNews Sentiment: {avg_sentiment}\nRSI: {rsi}\nEMA: {ema}")
    else:
        stock_label.config(text="Invalid Stock Symbol or API Error")

# Initialize the Tkinter window
root = tk.Tk()
root.title("Stock Analysis App")
root.geometry("400x400")

# Add a label to the window
label = tk.Label(root, text="Welcome to the Stock Analysis App", font=("Arial", 16), fg="blue")
label.pack(pady=10)

# Add an entry widget to input stock symbol
stock_entry = ttk.Entry(root, width=30, font=("Arial", 14))
stock_entry.pack(pady=10)
stock_entry.insert(0, "Enter Stock Symbol")

# Add a button to fetch stock data
fetch_button = ttk.Button(root, text="Fetch Data", command=fetch_stock_data)
fetch_button.pack(pady=10)

# Add a label to display stock data
stock_label = tk.Label(root, text="", font=("Arial", 12), fg="green")
stock_label.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
