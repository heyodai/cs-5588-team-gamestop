import streamlit as st
import pandas as pd
import ollama
import requests
import json
import time
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np


# Streamlit app definition
def main():
    st.title("📈🚀 MarketPulse")

    # Initialize progress bar and message holder at the top
    progress_bar = st.empty()
    success_placeholder = st.empty()

    # Sidebar for user input
    with st.sidebar:
        st.header("⚙️ Simulation Settings")

        start_date = st.date_input(
            "Start Date",
            value=pd.to_datetime("2018-01-01"),
            min_value=pd.to_datetime("2018-01-01"),
            max_value=pd.to_datetime("2020-01-01"),
        )
        end_date = st.date_input(
            "End Date",
            value=pd.to_datetime("2018-02-01"),
            min_value=pd.to_datetime("2018-01-01"),
            max_value=pd.to_datetime("2020-01-01"),
        )
        model = "llama3.2:3b"  # This could be an option in the future
        ticker = st.selectbox("Ticker", ["AAPL", "AMZN", "MSFT", "NVDA"])
        funds = st.number_input("Starting Funds", min_value=100, value=1000, step=100)
        risk = st.selectbox("Risk Tolerance", ["LOW", "MEDIUM", "HIGH"])

    # Initialize the Portfolio
    start_data = requests.get(
        f"http://localhost:8000/{ticker}/2018-01-02"
    ).json()  # TODO: make date dynamic
    p = Portfolio(
        ticker=ticker,
        funds=funds,
        holdings=100,
        risk=risk,
        price=start_data["prices"][0]["open"],
    )

    # Dates range for simulation
    dates = pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d")

    # DataFrame to store the results
    df = pd.DataFrame(
        columns=[
            "date",
            "price",
            "action",
            "volume",
            "value",
            "holdings",
            "funds",
            "reason",
        ]
    )

    # Real-time display
    chart_placeholder = st.empty()
    reasoning_placeholder = st.empty()

    # Progress bar setup
    progress = progress_bar.progress(0)
    total_steps = len(dates)

    # Simulation loop
    for step, date in enumerate(dates):
        if not was_market_open(date):
            continue

        news_data = ""
        data = requests.get(f"http://localhost:8000/{ticker}/{date}").json()

        for news in data["news"]:
            news_data += f"""
                ### {news["title"]}
                
                {news["summary"]}
            """

        factors = load_factors(p.ticker, date)
        lstm_prediction, actual_next_open_price = pseudo_lstm(p.ticker, date)
        prompt = generate_prompt(p, factors, date, lstm_prediction)
        response = query_ollama(prompt, model)

        try:
            response_data = json.loads(response)

            action = response_data["action"].lower()
            volume = int(response_data["volume"]) if "volume" in response_data else 0
            reason = response_data["reason"] if "reason" in response_data else ""
        except:
            action = "hold"
            volume = 0
            reason = ""

        price = data["prices"][0]["open"]

        if action == "buy":
            p.buy(volume, price)
            action_desc = "BUY"
        else:
            p.sell(volume, price)
            action_desc = "SELL"

        new_row = pd.DataFrame(
            {
                "date": date,
                "price": round(price, 2),
                "action": action_desc,
                "volume": volume if action in ["buy", "sell"] else 0,
                "value": round(p.value, 2),
                "holdings": p.holdings,
                "funds": round(p.funds, 2),
                "reason": reason,
                "predicted_price": lstm_prediction,
                "actual_next_open_price": actual_next_open_price,
            },
            index=[0],
        )
        df = pd.concat([df, new_row], ignore_index=True)

        # Update chart and reasoning in real time
        update_chart(df, chart_placeholder)
        update_reasoning(df, reasoning_placeholder)

        # Update the progress bar
        progress.progress((step + 1) / total_steps)

    # Save the results to a CSV file at the end of the simulation
    epoch = int(time.time())
    df.to_csv(f"{ticker}-{model}-{risk}-{epoch}.csv", index=False)

    # Display the success message at the top
    success_placeholder.success("🤑 Simulation completed!")


def pseudo_lstm(ticker, date):
    # TODO: Implement a real LSTM model

    # Open the CSV file and read the data
    data_fp = "/Users/odai/datasets/CMIN/CMIN-US/price/raw"  # TODO: make this dynamic
    df = pd.read_csv(f"{data_fp}/{ticker}.csv")

    # Find the row for the given date
    row = df[df["Date"] == date]
    row_idx = row.index[0]

    # Get the opening price for the next day
    next_row = df.iloc[row_idx + 1]
    prediction = round(next_row["Open"], 2)

    # Randomly add noise to the prediction
    noisy_prediction = prediction
    noisy_prediction += round(prediction * (0.1 * (2 * np.random.random() - 1)), 2)
    return prediction, noisy_prediction


# Function to generate prompt for model
def generate_prompt(p, factors, date, lstm):
    return f"""
        Today is {date} and you have {p.funds} to invest in {p.ticker}. You currently have {p.holdings} shares of {p.ticker} valued at {p.value}. Your portfolio risk tolerance is {p.risk}. Your LSTM model predicts that the opening price of {p.ticker} tomorrow will be {lstm}.

        The following are the top factors that may affect the stock price of {p.ticker} today:

        {factors}

        Please decide whether to buy or sell your shares of {p.ticker} for tomorrow. Please make sure not to buy more shares than you can afford or sell more shares than you own.
        
        Do NOT hold. You MUST buy or sell shares.
        
        Please reply in structured JSON, like so:
        {{
            "action": "buy",
            "volume": 10,
            "reason": "I think the stock price will go up based on the factors extracted..."
        }}
    """


# Function to update chart with horizontal plots and theme adjustment for dark mode
def update_chart(df, placeholder):
    # Set the color scheme
    dark_background = "#0E1117"
    plt.style.use("default")  # Start with the default style, then modify
    # plt.rcParams.update(
    #     {
    #         "axes.facecolor": dark_background,  # Background of the plot area
    #         "figure.facecolor": dark_background,  # Background of the entire figure
    #         "axes.edgecolor": "white",  # Color of the axes lines
    #         "xtick.color": "white",  # Color of x-axis tick labels
    #         "ytick.color": "white",  # Color of y-axis tick labels
    #         "axes.labelcolor": "white",  # Color of x and y axis labels
    #         "text.color": "white",  # Color of the title and text in the chart
    #         "legend.facecolor": dark_background,  # Legend background color
    #     }
    # )

    # Create a 1-row, 3-column layout for horizontal charts
    fig, ax = plt.subplots(1, 3, figsize=(18, 6))

    # First chart: Funds over time
    ax[0].plot(df["date"], df["funds"], color="cyan")
    ax[0].set_xlabel("Date")
    ax[0].set_ylabel("Funds ($)")
    ax[0].set_title("Funds Over Time")
    ax[0].tick_params(axis="x", rotation=45)  # Rotate x-axis labels for readability

    # Second chart: Holdings over time
    ax[1].plot(df["date"], df["holdings"], color="lime")
    ax[1].set_xlabel("Date")
    ax[1].set_ylabel("Holdings (Shares)")
    ax[1].set_title("Holdings Over Time")
    ax[1].tick_params(axis="x", rotation=45)  # Rotate x-axis labels for readability

    # Third chart: Portfolio Value over time
    ax[2].plot(df["date"], df["value"], color="orange")
    ax[2].set_xlabel("Date")
    ax[2].set_ylabel("Portfolio Value ($)")
    ax[2].set_title("Portfolio Value Over Time")
    ax[2].tick_params(axis="x", rotation=45)  # Rotate x-axis labels for readability

    plt.tight_layout()  # Adjust layout to prevent overlap
    placeholder.pyplot(fig)


# Function to update reasoning log
def update_reasoning(df, placeholder):
    reasoning_log = ""

    # Reverse the DataFrame to display the newest days first
    df_reversed = df.iloc[::-1]

    for _, row in df_reversed.iterrows():
        reasoning_log += f"### {row['date']}\n\n"
        reasoning_log += f"{row['reason']}\n\n"

        # Add a bullet-point list with key info for that day
        reasoning_log += f"- **Price**: {row['price']}\n"
        reasoning_log += f"- **Action**: {row['action']}\n"
        reasoning_log += f"- **Volume**: {row['volume']}\n"
        reasoning_log += f"- **Value**: {row['value']}\n"
        reasoning_log += f"- **Holdings**: {row['holdings']}\n"
        reasoning_log += f"- **Funds**: {row['funds']}\n"

        # Add a horizontal separator
        reasoning_log += "---\n"

    # Display the formatted reasoning log using Markdown
    placeholder.markdown(reasoning_log)


# Helper function to query Ollama API
def query_ollama(prompt, model):
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return response["message"]["content"]


# Helper function to check if the market was open
def was_market_open(date):
    df = pd.read_csv("data/were-markets-open.csv")
    df = df[df["was_open"]]
    return date in df["date"].values


# Load factors from file (simulating the extracted data)
def load_factors(ticker, date):
    path = f"data/factors/{ticker}-{date}.md"
    with open(path, "r") as f:
        return f.read()


# Portfolio class definition
class Portfolio:
    def __init__(self, ticker, funds, holdings, risk, price):
        self.ticker = ticker
        self.funds = funds
        self.holdings = holdings
        self.value = funds + holdings * price
        self.risk = risk

    def buy(self, amount, price):
        max_affordable = int(self.funds / price)
        if amount > max_affordable:
            amount = max_affordable
        self.holdings += amount
        self.funds -= amount * price
        self.value = self.funds + self.holdings * price

    def sell(self, amount, price):
        if amount > self.holdings:
            amount = self.holdings
        self.holdings -= amount
        self.funds += amount * price
        self.value = self.funds + self.holdings * price


# Run the app
if __name__ == "__main__":
    main()
