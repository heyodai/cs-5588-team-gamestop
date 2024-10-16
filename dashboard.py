import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data and ensure the date column is in datetime format
data = {
    'date': ['2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05', '2018-01-08'],
    'price': [42.54, 43.13, 43.13, 43.36, 43.59],
    'action': ['HOLD', 'SELL', 'BUY', 'HOLD', 'BUY'],
    'volume': [0, 50, 5, 0, 20],
    'value': [1000, 5313.25, 5313.37, 5313.37, 5338.26],
    'holdings': [100, 50, 55, 55, 75],
    'funds': [1000, 3156.625, 2940.95001, 2940.95001, 2069.19997],
    'reason': [
        "High portfolio risk tolerance and current market trends suggest selling AAPL...",
        "Despite a strong start to the year, there is no clear indication...",
        "The disclosed security flaws, particularly the 'Meltdown' bug...",
        "No new action",
        "Despite increasing competition from Google and Samsung..."
    ]
}

df = pd.DataFrame(data)

# Convert 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Set page configuration
st.set_page_config(page_title="Stock Trading Simulation", layout="wide")

# Title and description
st.title("📈 Stock Trading Simulation Dashboard")
st.write("This dashboard shows a day-by-day simulation of a stock trading portfolio based on market conditions, price movements, and decisions.")

# Sidebar for navigation
st.sidebar.title("Navigation")

# Date range filter
st.sidebar.subheader("Filter by Date Range")
start_date = st.sidebar.date_input("Start date", df['date'].min())
end_date = st.sidebar.date_input("End date", df['date'].max())

# Filter the dataframe based on the date range
if start_date > end_date:
    st.error("Error: End date must be after start date.")
else:
    filtered_df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

    # Display filtered data
    st.write(f"Showing data from **{start_date}** to **{end_date}**")

    # Select a date from the filtered date range
    selected_date = st.sidebar.selectbox("Select a date", filtered_df['date'].dt.strftime('%Y-%m-%d'))

    # Display the details for the selected day
    st.subheader(f"Details for {selected_date}")
    selected_row = filtered_df[filtered_df['date'] == pd.to_datetime(selected_date)]

    # Use columns for a clean layout
    col1, col2, col3 = st.columns(3)

    col1.metric(label="Action", value=selected_row['action'].values[0])
    col2.metric(label="Price", value=f"${selected_row['price'].values[0]:,.2f}")
    col3.metric(label="Volume", value=selected_row['volume'].values[0])

    st.write(f"**Reason for Action:** {selected_row['reason'].values[0]}")

    # Chart: Holdings over time
    st.subheader("📊 Holdings Over Time")

    fig, ax = plt.subplots()
    ax.plot(filtered_df['date'], filtered_df['holdings'], marker='o', linestyle='-', color='blue')
    ax.set_xlabel("Date")
    ax.set_ylabel("Holdings")
    ax.set_title("Holdings Over Time")
    ax.grid(True)

    # Display the chart
    st.pyplot(fig)

    # Chart: Funds over time
    st.subheader("💰 Funds Over Time")

    fig, ax = plt.subplots()
    ax.plot(filtered_df['date'], filtered_df['funds'], marker='o', linestyle='-', color='green')
    ax.set_xlabel("Date")
    ax.set_ylabel("Funds")
    ax.set_title("Funds Over Time")
    ax.grid(True)

    # Display the chart
    st.pyplot(fig)
