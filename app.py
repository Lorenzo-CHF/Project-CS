import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

def get_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
    return stock_data

def plot_stock_comparison(stock_data, tickers):
    fig = px.line(stock_data, x=stock_data.index, y=stock_data.columns, labels={'value': 'Stock Price'})
    fig.update_layout(title='Stock Comparison', xaxis_title='Date', yaxis_title='Stock Price')
    fig.update_traces(mode='lines', hovertemplate='Date: %{x}<br>Stock Price: %{y}')
    fig.update_layout(legend=dict(title='Stock Tickers', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    return fig

# Streamlit app
st.title('Stock Comparison App')

# Sidebar for user input
st.sidebar.header('User Input')

start_date = st.sidebar.date_input('Start Date', pd.to_datetime('2022-01-01'))
end_date = st.sidebar.date_input('End Date', pd.to_datetime('2023-01-01'))

# User input for multiple stock tickers
tickers = st.sidebar.text_input('Enter stock tickers (comma-separated)', 'AAPL,GOOGL,MSFT').split(',')

# Fetch data for each stock
stock_data = pd.DataFrame()
for ticker in tickers:
    stock_data[ticker] = get_stock_data(ticker, start_date, end_date)

# Plot the comparison chart
if not stock_data.empty:
    st.plotly_chart(plot_stock_comparison(stock_data, tickers))
else:
    st.warning('Enter valid stock tickers.')
