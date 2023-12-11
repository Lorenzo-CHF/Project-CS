# streamlit_app.py

import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests

supabase: Client = create_client("https://pulfkaxpvhgvgvlgjpaj.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB1bGZrYXhwdmhndmd2bGdqcGFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDIxNTkzNzIsImV4cCI6MjAxNzczNTM3Mn0.twkOSqpf4M7qVREItNHb19rG7iWNli-dtc2DSdEdBlQ")

# Initialize the session state variable if not present
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# Get the current user's username
myUserName = st.session_state.get('username')
st.title("Hello " + myUserName)

tab1, tab2 = st.tabs(["Portfolio Tracker", "Information Tool"])
if myUserName == "":
    # region USER IS NOT LOGGED IN
    with st.form("Login"):
        enteredUsername = st.text_input("Enter your username")
        submitted = st.form_submit_button("Login")
        if submitted:
            st.session_state['username'] = enteredUsername
    # endregion
else:
    # region USER IS LOGGED IN
    with tab1:
        # region Add Holding Form
        with st.form("Add Holding"):
            # Input fields to collect the data from the user
            symbol = st.text_input("Enter Stock Symbol")
            amount_of_shares = st.number_input("Enter the Number of Shares", min_value=0.01, step=0.01, format="%.2f")
            purchase_date = st.date_input("Select Purchase Date")
            
            # Form submission button
            submitted = st.form_submit_button("Add Holding")

        if submitted:
            # Convert the date to a string in ISO format before sending it to Supabase
            formatted_purchase_date = purchase_date.isoformat() if isinstance(purchase_date, date) else purchase_date
            
            response = supabase.table("portfolio").insert(
                {
                    "stock_symbol": symbol, 
                    "quantity": amount_of_shares, 
                    "purchase_date": formatted_purchase_date,
                    "username": myUserName
                }
            ).execute()
            st.write("Holding added!")
        # endregion

        # region Holdings Table
        # Execute the query to fetch all data from the 'portfolio' table
        response = supabase.table("portfolio").select("*").eq("username", myUserName).execute()

        # Display the filtered data
        st.header("Your holdings")
        for holding in response.data:
            col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
            with col1:
                st.write(holding['stock_symbol'])
            with col2:
                st.write(holding['quantity'])
            with col3:
                st.write(holding['purchase_date'])
            with col4:
                # Use a unique key for each button
                if st.button("Delete", key=f"delete_{holding['id']}"):
                    response = supabase.table("portfolio").delete().eq('id', holding['id']).execute()
                    st.rerun()
        # endregion
        
        # region Portfolio Value Chart
        total_values = pd.DataFrame()
        response = supabase.table("portfolio").select("id","stock_symbol", "quantity", "purchase_date").eq("username", myUserName).execute()
        for holding in response.data:
            stock = yf.Ticker(holding['stock_symbol'])
            data = stock.history(start=holding['purchase_date'])
            holding_value = data['Close'] * holding['quantity']
            holding_value.name = holding['stock_symbol']+" " + holding['purchase_date']  # Naming the series with the symbol for identification
            if total_values.empty:
                total_values = holding_value.to_frame()
            else:
                total_values = total_values.join(holding_value, how='outer')



        # Sum across columns to get the total portfolio value
        if not total_values.empty:
            total_values['Total Value'] = total_values.sum(axis=1)
            # Format the index to display only year, month, and day
            total_values.index = total_values.index.date
            # Display data as a line chart
            st.line_chart(total_values['Total Value'])
            # Display the data in a table format and show the stock symbols as columns
            st.dataframe(total_values, width=700, height=300)
        # endregion

        with tab2:
        # Function to format camelCase names into a readable format https://python-yahoofinance.readthedocs.io/en/latest/
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
            

                # NewsAPI key
            news_api_key = 'd3e1cfc10e9e472ca85a16f294c9dc78'

            # Function to fetch news https://newsapi.org/docs
            def get_stock_news(symbol):
                base_url = "https://newsapi.org/v2/everything?"
                query = f"q={symbol}&apiKey={news_api_key}"
                response = requests.get(base_url + query)
                articles = response.json().get('articles', [])
                return articles[:5]  # Return top 5 articles

            # Display news for the selected stock
            news_symbol = st.sidebar.text_input("Enter Stock Symbol for News")
            if news_symbol:
                    st.sidebar.write(f"Latest News for {news_symbol}:")
                    news_items = get_stock_news(news_symbol)
                    for item in news_items:
                            st.sidebar.write(f"**{item['title']}**")
                            st.sidebar.write(item['description'])
                            st.sidebar.write(f"[Read more]({item['url']})", unsafe_allow_html=True)
                            st.sidebar.write("---")




            # Initialize session state for stock symbols
            if 'num_stocks' not in st.session_state:
                st.session_state['num_stocks'] = 1  # Start with 1 stock
            # Fetch data for a sample stock to get all data points
            sample_stock = yf.Ticker('AAPL')
            sample_data = sample_stock.info
            # Extract and format all available data points
            all_data_points = [format_camel_case(point) for point in sample_data.keys()]
            # Multiselect dropdown for choosing data points
            selected_data_points = st.multiselect('Select data points for comparison', all_data_points, default=['Current Price', 'Market Cap', 'Sector', 'Dividend Yield', 'Payout Ratio', 'Currency', 'Price To Book'])
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
    # endregion
