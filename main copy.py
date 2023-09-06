import tkinter as tk
import requests
import json
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from alpha_vantage.timeseries import TimeSeries
from tkinter import ttk

NEWS_API_KEY = "YOUR_NEWS_API_KEY"

# Initialize sentiment analysis analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

def fetch_news(stock_symbol):
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = json.loads(response.text)
    headlines = [article['title'] for article in data['articles'][:5]]
    return headlines

def analyze_sentiment(stock_data, news_headlines):
    df = pd.DataFrame(stock_data).T.astype(float)
    close_prices = df["4. close"]
    
    moving_average = round(close_prices.mean(), 4)
    avg_volume = round(df["5. volume"].mean(), 4)
    ema_9 = round(close_prices.ewm(span=9, adjust=False).mean().iloc[-1], 4)
    ema_21 = round(close_prices.ewm(span=21, adjust=False).mean().iloc[-1], 4)
    rsi = calculate_rsi(close_prices, 14)
    
    news_sentiment = [sentiment_analyzer.polarity_scores(headline)['compound'] for headline in news_headlines]
    avg_sentiment = round(sum(news_sentiment) / len(news_sentiment), 4)
    
    sentiment = "Undecided"
    confidence = 0.5
    
    if moving_average > ema_21 and avg_volume > 1000 and avg_sentiment > 0.6 and rsi < 70 and ema_9 > moving_average:
        sentiment = "Buy"
        confidence = 0.9
    elif moving_average < ema_9 and avg_volume < 1000 and avg_sentiment < 0.4 and rsi > 30 and ema_9 < moving_average:
        sentiment = "Sell"
        confidence = 0.8
    
    return sentiment, confidence, moving_average, avg_volume, avg_sentiment, rsi, ema_9, ema_21

def fetch_stock_data():
    stock_symbol = stock_var.get()
    print(f"Fetching data for {stock_symbol}")
    
    ts = TimeSeries(key='YOUR_ALPHA_VANTAGE_API_KEY', output_format='pandas')
    data, _ = ts.get_intraday(symbol=stock_symbol, interval='5min')
    
    news_headlines = fetch_news(stock_symbol)
    
    if not data.empty:
        sentiment, confidence, moving_average, avg_volume, avg_sentiment, rsi, ema_9, ema_21 = analyze_sentiment(data, news_headlines)
        stock_label.config(text=f"Sentiment: {sentiment}
Confidence: {confidence * 100}%
Moving Average: {moving_average}
Average Volume: {avg_volume}
News Sentiment: {avg_sentiment}
RSI: {rsi}
EMA 9: {ema_9}
EMA 21: {ema_21}")
    else:
        stock_label.config(text="Invalid Stock Symbol or API Error")

# Initialize the Tkinter window
root = tk.Tk()
root.title("Stock Analysis App")
root.geometry("400x400")

# Add a label to the window
label = tk.Label(root, text="Welcome to the Stock Analysis App", font=("Arial", 16), fg="blue")
label.pack(pady=10)

# Add a dropdown menu to select stock symbol
stock_var = tk.StringVar()
stock_choices = ["AAPL", "GOOG", "TSLA", "AMZN"]
stock_dropdown = ttk.OptionMenu(root, stock_var, *stock_choices)
stock_dropdown.pack(pady=10)

# Add a button to fetch stock data
fetch_button = ttk.Button(root, text="Fetch Data", command=fetch_stock_data)
fetch_button.pack(pady=10)

# Add a label to display stock data
stock_label = tk.Label(root, text="", font=("Arial", 12), fg="green")
stock_label.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()