import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Function to format camelCase names into a readable format
def format_camel_case(name):
    formatted_name = ''.join([' ' + char if char.isupper() else char for char in name]).strip()
    return formatted_name.title()

# Function to fetch stock data
def fetch_stock_data(symbol):
    stock = yf.Ticker(symbol)
    return stock.info

# Function to get the original key from formatted name
def get_original_key(formatted_name, sample_data):
    for key in sample_data.keys():
        if format_camel_case(key) == formatted_name:
            return key
    return None

# Initialize session state for stock symbols
if 'num_stocks' not in st.session_state:
    st.session_state['num_stocks'] = 1  # Start with 1 stock

# Fetch data for a sample stock to get all data points
sample_stock = yf.Ticker('AAPL')
sample_data = sample_stock.info

# Extract and format all available data points
all_data_points = [format_camel_case(point) for point in sample_data.keys()]

# Multiselect dropdown for choosing data points
selected_data_points = st.multiselect('Select data points for comparison', all_data_points, default=['Current Price', 'Market Cap', 'Sector', 'Dividend Rate', 'Dividend Yield', 'Payout Ratio', 'Volume', 'Currency', 'Price To Book'])

# Function to add more stocks
def add_stock():
    st.session_state['num_stocks'] += 1

# Button to add more stocks
st.button('Add another stock', on_click=add_stock)

# Create input fields dynamically based on the number of stocks
stock_symbols = []
for i in range(st.session_state['num_stocks']):
    symbol = st.text_input(f'Stock Symbol {i + 1}', key=f'stock_{i}')
    if symbol:
        stock_symbols.append(symbol)

# Fetch data for entered symbols
stock_data = [fetch_stock_data(symbol) for symbol in stock_symbols if symbol]

# Only proceed if at least one stock has been entered
if stock_data:
    # Adjust the data fetching to use the original keys
    comparison_data = {'Data Point': selected_data_points}
    for symbol, data in zip(stock_symbols, stock_data):
        comparison_data[symbol] = [data.get(get_original_key(point, sample_data)) for point in selected_data_points]

    # Create the DataFrame
    comparison_df = pd.DataFrame(comparison_data)

    # Styling the DataFrame
    st.write(comparison_df.style.set_properties(**{'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'}).set_table_styles([{'selector': 'th', 'props': [('font-size', '16px')]}]))

# Function to fetch YTD stock price data and normalize it
def fetch_normalize_stock_data(symbol):
    today = datetime.today().strftime('%Y-%m-%d')
    start_of_year = datetime.today().replace(month=1, day=1).strftime('%Y-%m-%d')
    stock = yf.Ticker(symbol)
    df = stock.history(start=start_of_year, end=today)
    # Normalize to 100 at the starting point
    normalized_df = (df['Close'] / df['Close'].iloc[0]) * 100
    return normalized_df

# Fetch and plot data if at least one stock has been entered
if stock_data:
    plt.figure(figsize=(10, 6))
    for symbol in stock_symbols:
        normalized_prices = fetch_normalize_stock_data(symbol)
        plt.plot(normalized_prices, label=symbol)

    plt.title("YTD Stock Price Comparison, Normalized to 100")
    plt.xlabel("Date")
    plt.ylabel("Normalized Price")
    plt.legend()
    st.pyplot(plt)
