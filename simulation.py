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
st.title("🚀 MarketPulse 🚀")

with st.sidebar:
    st.sidebar.header("⚙️ Simulation Settings")

    # Date input widgets
    start_date = st.date_input("Start Date", datetime.date(2021, 1, 1))
    end_date = st.date_input("End Date", datetime.date(2021, 12, 31))

    # Starting funds input
    starting_funds = st.number_input("Starting Funds", value=STARTING_FUNDS)
    # Update the portfolio funds if changed
    if starting_funds != STARTING_FUNDS:
        STARTING_FUNDS = starting_funds
        portfolio.funds = STARTING_FUNDS

    # Risk tolerance input
    risk_tolerance = st.selectbox("Risk Tolerance", options=["LOW", "MID", "HIGH"])
    
    # Stock selection checkboxes
    st.sidebar.subheader("Select Stocks to Trade")
    tradeable_stocks = {
        'AAPL': st.checkbox("Apple (AAPL)", value=True),
        'JNJ': st.checkbox("Johnson & Johnson (JNJ)", value=True),
        'CVX': st.checkbox("Chevron (CVX)", value=True),
        'BAC': st.checkbox("Bank of America (BAC)", value=True),
        'WMT': st.checkbox("Walmart (WMT)", value=True)
    }
    selected_stocks = [ticker for ticker, is_selected in tradeable_stocks.items() if is_selected]

# Validate date input
if start_date > end_date:
    st.error("Error: Start date must be before end date.")
    st.stop()

# %%
# Prepare to store portfolio values and decisions
dates = pd.date_range(start_date, end_date)
portfolio_values = []
funds_values = []
stock_values = []
decisions = []

st.header("Simulation Progress")
progress_bar = st.progress(0)

# Display charts side by side
st.header("Portfolio Value Over Time")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("💸 Funds")
    funds_chart = st.line_chart(pd.DataFrame({"value": []}), color="#00ff00")
with col2:
    st.subheader("📈 Stock Value")
    stock_chart = st.line_chart(pd.DataFrame({"value": []}))
with col3:
    st.subheader("💰 Total Portfolio Value")
    total_value_chart = st.line_chart(pd.DataFrame({"value": []}))

for idx, date in enumerate(dates):
    date_str = date.strftime("%Y-%m-%d")

    # Check if the market was open on this date
    if date not in market_open_df.index or not market_open_df.loc[date, "was_open"]:
        st.subheader(f"❌ Date: {date_str}")
        st.write(f"Market closed on {date_str}. Skipping this day.")
        continue
    
    st.subheader(f"📅 Date: {date_str}")

    # Get market info
    market_info = market.get_info(date_str)

    # Get portfolio makeup
    portfolio_makeup = portfolio.get_makeup()

    # Get the prompt for the LLM with risk tolerance
    prompt = llm.get_prompt(
        date_str,
        json.dumps(market_info),
        portfolio.funds,
        portfolio_makeup,
        risk_tolerance=risk_tolerance,  # Pass the risk tolerance level
        market_factors=None,  # If you have market factors
        world_factors=None,  # If you have world factors
    )

    # Execute the prompt and get the LLM's decision
    llm_response = llm.execute_prompt(prompt)
    decisions.append((date_str, llm_response))

    # Display the LLM's decision
    st.write(f"🤖 LLM Decision:\n```{llm_response}\n```")

    # Parse the LLM's decision and update the portfolio
    try:
        actions = json.loads(llm_response)
        for action in actions:
            ticker = action["ticker"]
            
            if ticker not in ['AAPL', 'JNJ', 'CVX', 'BAC', 'WMT']:
                # TODO: This is a band-aid fix.
                continue
            
            amount = action["amount"]
            if action["type"].lower() == "buy":
                stock_value = market.stocks[ticker].get_prices(date_str)[0]["close"]
                portfolio.buy_stock(ticker, amount, stock_value)
            elif action["type"].lower() == "sell":
                portfolio.sell_stock(ticker, amount)
            else:
                st.warning(f"Unknown action type: {action['type']}")
    except Exception as e:
        st.error(f"Error parsing LLM response on {date_str}: {e}")

    for ticker in portfolio.stocks:
        prices = market.stocks[ticker].get_prices(date_str)
        if prices:
            new_value = prices[0]["close"]
            portfolio.update_stock_value(ticker, new_value)
        else:
            st.error(f"Price data for {ticker} on {date_str} is missing.")

    # Update portfolio values
    funds = portfolio.funds
    stock_value = portfolio.get_stock_value()
    total_value = portfolio.get_value()

    # Append values to lists
    funds_values.append({"date": date_str, "value": funds})
    stock_values.append({"date": date_str, "value": stock_value})
    portfolio_values.append({"date": date_str, "value": total_value})

    # Update each chart dynamically
    funds_chart.add_rows(pd.DataFrame([{"date": date, "value": funds}]).set_index("date"))
    stock_chart.add_rows(pd.DataFrame([{"date": date, "value": stock_value}]).set_index("date"))
    total_value_chart.add_rows(pd.DataFrame([{"date": date, "value": total_value}]).set_index("date"))

    # Update progress bar
    progress_bar.progress((idx + 1) / len(dates))

# %%
# Final portfolio values data frames
df_portfolio = pd.DataFrame(portfolio_values)
df_funds = pd.DataFrame(funds_values)
df_stocks = pd.DataFrame(stock_values)

# Set the date column as the index for each dataframe
df_portfolio["date"] = pd.to_datetime(df_portfolio["date"])
df_portfolio = df_portfolio.set_index("date")

df_funds["date"] = pd.to_datetime(df_funds["date"])
df_funds = df_funds.set_index("date")

df_stocks["date"] = pd.to_datetime(df_stocks["date"])
df_stocks = df_stocks.set_index("date")
