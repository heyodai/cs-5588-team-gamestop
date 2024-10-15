import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd

# Streamlit page configuration
st.set_page_config(page_title="Stock Data Viewer", layout="wide")

# Title
st.title("Stock Data Viewer")

# Sidebar for input
st.sidebar.header("Input Options")
ticker = st.sidebar.text_input("Ticker", value="AAPL").upper()
input_date = st.sidebar.date_input("Date", value=datetime(2018, 1, 2))
increment = st.sidebar.selectbox("Change Date By:", options=["Previous Day", "Next Day"])

# Function to handle date incrementing
def increment_date(date, change):
    if change == "Previous Day":
        return date - timedelta(days=1)
    elif change == "Next Day":
        return date + timedelta(days=1)
    return date

# Increment or decrement the date based on selection
if st.sidebar.button("Apply Date Change"):
    input_date = increment_date(input_date, increment)

# Convert date to string for the API request
date_str = input_date.strftime("%Y-%m-%d")

# Function to fetch data from FastAPI
def fetch_data(ticker, date):
    url = f"http://localhost:8000/{ticker}/{date}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        st.error(f"An error occurred: {err}")

# Fetching and displaying the data
data = fetch_data(ticker, date_str)

if data:
    st.write("## Price Data")
    if data["prices"]:
        st.json(data["prices"])
    else:
        st.write("No price data available for this date.")

    st.write("## News")
    if data["news"]:
        for news_item in data["news"]:
            st.write(f"#### {news_item['title']}")
            st.write(news_item['summary'])
    else:
        st.write("No news data available for this date.")

# Reminder to run the FastAPI locally
st.sidebar.markdown(
    """
    Ensure that the FastAPI server is running locally on port 8000 for this app to function properly.
    """
)
