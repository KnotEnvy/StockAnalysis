import tkinter as tk
import requests
import json

API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"

def analyze_sentiment(latest_close_price):
    # Placeholder for a more complex sentiment analysis
    if float(latest_close_price) > 100:
        return "Buy", 0.9  # Sentiment, Confidence
    elif float(latest_close_price) < 50:
        return "Sell", 0.8
    else:
        return "Undecided", 0.7

def fetch_stock_data():
    stock_symbol = stock_entry.get()
    print(f"Fetching data for {stock_symbol}")
    
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval=5min&apikey={API_KEY}"
    response = requests.get(url)
    data = json.loads(response.text)
    
    if "Time Series (5min)" in data:
        latest_close_price = data["Time Series (5min)"][list(data["Time Series (5min)"].keys())[0]]["4. close"]
        sentiment, confidence = analyze_sentiment(latest_close_price)
        stock_label.config(text=f"Latest Close Price: {latest_close_price}\nSentiment: {sentiment}\nConfidence: {confidence * 100}%")
    else:
        stock_label.config(text="Invalid Stock Symbol or API Error")

# Initialize the Tkinter window
root = tk.Tk()
root.title("Stock Analysis App")

# Add a label to the window
label = tk.Label(root, text="Welcome to the Stock Analysis App")
label.pack()

# Add an entry widget to input stock symbol
stock_entry = tk.Entry(root, width=50)
stock_entry.pack()
stock_entry.insert(0, "Enter Stock Symbol")

# Add a button to fetch stock data
fetch_button = tk.Button(root, text="Fetch Data", command=fetch_stock_data)
fetch_button.pack()

# Add a label to display stock data
stock_label = tk.Label(root, text="")
stock_label.pack()

# Run the Tkinter event loop
root.mainloop()
