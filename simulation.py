# %%
import streamlit as st
import pandas as pd
import datetime
import json

# Import custom classes
from src.market import Market
from src.portfolio import Portfolio
from src.llm import LanguageModel

# %%
# Constants and configurations
DATASET_FP = "/Users/odai/repos/cs-5588-team-gamestop/datasets/CMIN-US"
STARTING_FUNDS = 10_000  # USD
# LLM_MODEL = "llama3.2:3b"
LLM_MODEL = "qwen2.5:1.5b"

# Initialize instances
market = Market(DATASET_FP)
portfolio = Portfolio()
portfolio.add_funds(STARTING_FUNDS)
llm = LanguageModel(LLM_MODEL, "src/prompt-templates/system-prompt.txt")

# Load market open/closed data
market_open_df = pd.read_csv("research/were-markets-open.csv")
market_open_df["date"] = pd.to_datetime(market_open_df["date"])
market_open_df = market_open_df.set_index("date")

# %%
# Set the page configuration
st.set_page_config(page_title="LLM Stock Trading Simulation", layout="wide")

# %%
# Title of the app
st.title("💹 MarketPulse 📈")

with st.sidebar:
    st.sidebar.header("⚙️ Simulation Settings")

    # Date input widgets
    start_date = st.date_input("Start Date", datetime.date(2018, 1, 1))
    end_date = st.date_input("End Date", datetime.date(2018, 1, 7))

    # Starting funds input
    starting_funds = st.number_input("Starting Funds", value=10000)
    # Update the portfolio funds if changed
    if starting_funds != STARTING_FUNDS:
        STARTING_FUNDS = starting_funds
        portfolio.funds = STARTING_FUNDS

# Validate date input
if start_date > end_date:
    st.error("Error: Start date must be before end date.")
    st.stop()

# %%
# Prepare to store portfolio values and decisions
dates = pd.date_range(start_date, end_date)
portfolio_values = []
decisions = []

st.header("Simulation Progress")

# Progress bar
progress_bar = st.progress(0)

for idx, date in enumerate(dates):
    date_str = date.strftime("%Y-%m-%d")

    st.subheader(f"📅 Date: {date_str}")

    # Check if the market was open on this date
    if date not in market_open_df.index or not market_open_df.loc[date, "was_open"]:
        st.write(f"Market closed on {date_str}. Skipping this day.")
        continue

    # Get market info
    market_info = market.get_info(date_str)

    # Get portfolio makeup
    portfolio_makeup = portfolio.get_makeup()

    # Get the prompt for the LLM
    prompt = llm.get_prompt(
        date_str,
        json.dumps(market_info),
        portfolio.funds,
        portfolio_makeup,
        market_factors=None,  # If you have market factors
        world_factors=None,  # If you have world factors
    )

    # Execute the prompt and get the LLM's decision
    llm_response = llm.execute_prompt(prompt)
    decisions.append((date_str, llm_response))

    # Display the LLM's decision
    st.write("🤖 LLM Decision:\n" + llm_response)

    # Parse the LLM's decision and update the portfolio
    try:
        actions = json.loads(llm_response)
        for action in actions:
            ticker = action["ticker"]
            amount = action["amount"]
            if action["type"].lower() == "buy":
                stock_value = market.stocks[ticker].get_price(date_str)
                portfolio.buy_stock(ticker, amount, stock_value)
            elif action["type"].lower() == "sell":
                portfolio.sell_stock(ticker, amount)
            else:
                st.warning(f"Unknown action type: {action['type']}")
    except Exception as e:
        st.error(f"Error parsing LLM response on {date_str}: {e}")

    # Update stock values in the portfolio
    for ticker in portfolio.stocks:
        new_value = market.stocks[ticker].get_price(date_str)
        portfolio.update_stock_value(ticker, new_value)

    # Update portfolio value
    total_value = portfolio.get_value()
    portfolio_values.append({"date": date_str, "value": total_value})

    # Update progress bar
    progress_bar.progress((idx + 1) / len(dates))

# %%
st.header("💰 Portfolio Value Over Time")

df_portfolio = pd.DataFrame(portfolio_values)
df_portfolio["date"] = pd.to_datetime(df_portfolio["date"])
df_portfolio = df_portfolio.set_index("date")

st.line_chart(df_portfolio["value"])
