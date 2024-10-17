import streamlit as st
import pandas as pd
import ollama
import requests
import json
import time
from tqdm import tqdm
import matplotlib.pyplot as plt


# Streamlit app definition
def main():
    st.title("📈🚀 MarketPulse")

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
        model = st.selectbox(
            "Model", ["llama3.2:3b", "llama3.2:7b", "llama3.2:13b"]
        )  # TODO: Change models
        ticker = st.selectbox("Ticker", ["AAPL", "AMZN", "MSFT", "NVDA"])
        funds = st.number_input("Starting Funds", min_value=100, value=1000, step=100)
        risk = st.selectbox("Risk Tolerance", ["LOW", "MEDIUM", "HIGH"])

    # Initialize the Portfolio
    p = Portfolio(ticker=ticker, funds=funds, holdings=100, risk=risk)

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

    # Simulation loop
    for date in tqdm(dates):
        if not was_market_open(date):
            continue

        news_data = ""
        data = requests.get(f"http://localhost:8000/{ticker}/{date}")
        data = data.json()

        for news in data["news"]:
            news_data += f"""
                ### {news["title"]}
                
                {news["summary"]}
            """

        factors = load_factors(p.ticker, date)
        prompt = generate_prompt(p, factors, date)
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

        if action == "buy" and volume > 0:
            p.buy(volume, price)
            action_desc = "BUY"
        elif action == "sell" and volume > 0:
            p.sell(volume, price)
            action_desc = "SELL"
        else:
            action_desc = "HOLD"

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
            },
            index=[0],
        )
        df = pd.concat([df, new_row], ignore_index=True)

        # Update chart and reasoning in real time
        update_chart(df, chart_placeholder)
        update_reasoning(df, reasoning_placeholder)

    # Save the results to a CSV file at the end of the simulation
    epoch = int(time.time())
    df.to_csv(f"{ticker}-{model}-{risk}-{epoch}.csv", index=False)
    st.success("🤑 Simulation completed!")


# Function to generate prompt for model
def generate_prompt(p, factors, date):
    return f"""
        Today is {date} and you have {p.funds} to invest in {p.ticker}. You currently have {p.holdings} shares of {p.ticker} valued at {p.value}. Your portfolio risk tolerance is {p.risk}.

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


# Function to update chart
def update_chart(df, placeholder):
    fig, ax = plt.subplots()
    ax.plot(df["date"], df["funds"], label="Funds", color="blue")
    ax.plot(df["date"], df["holdings"], label="Holdings", color="green")
    ax.plot(df["date"], df["value"], label="Portfolio Value", color="orange")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value ($)")
    ax.legend()
    ax.set_title("Portfolio Over Time")
    plt.xticks(rotation=45)
    placeholder.pyplot(fig)


# Function to update reasoning log
def update_reasoning(df, placeholder):
    reasoning_log = ""
    for _, row in df.iterrows():
        reasoning_log += f"### {row['date']}\n\n{row['reason']}\n\n---\n"

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
    df = pd.read_csv("research/were-markets-open.csv")
    df = df[df["was_open"]]
    return date in df["date"].values


# Load factors from file (simulating the extracted data)
def load_factors(ticker, date):
    path = f"factors/{ticker}-{date}.md"
    with open(path, "r") as f:
        return f.read()


# Portfolio class definition
class Portfolio:
    def __init__(self, ticker, funds, holdings, risk):
        self.ticker = ticker
        self.funds = funds
        self.holdings = holdings
        self.value = funds
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
