# %%
from fastapi import FastAPI, HTTPException
from datetime import date
import pandas as pd

# %%
DATA_FP = "/Users/odai/datasets"
CMIN_FP = f"{DATA_FP}/CMIN/CMIN-US/news/raw"

app = FastAPI()

# %%
def get_news(ticker: str, date: str):
    # Load and process the data
    df = pd.read_csv(f"{CMIN_FP}/{ticker}.csv", sep="	")
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] == date]

    # Map rows to JSON
    news_json = []
    for i, rows in df.iterrows():
        news_json.append({"title": rows["title"], "summary": rows["summary"]})

    return news_json

# %%
def get_prices(ticker: str, date: str):
    # Load and process the data
    df = pd.read_csv(f"{DATA_FP}/CMIN/CMIN-US/price/raw/{ticker}.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[df["Date"] == date]

    # Map rows to JSON
    prices_json = []
    for i, rows in df.iterrows():
        prices_json.append(
            {
                "open": rows["Open"],
                "close": rows["Close"],
                "high": rows["High"],
                "low": rows["Low"],
                "volume": rows["Volume"],
            }
        )

    return prices_json

# %%
@app.get("/{ticker}/{date}")
async def get_data(ticker: str, date: str):
    news = get_news(ticker, date)
    prices = get_prices(ticker, date)
    
    # Check if the market was closed on this day
    if not prices:
        raise HTTPException(status_code=403, detail="Market was closed on this day")

    return {"ticker": ticker, "date": date, "news": news, "prices": prices}


