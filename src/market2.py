# %%
import pandas as pd
import json

# %%
class MarketStock:
    def __init__(self, ticker, dataset_fp):
        self.ticker = ticker
        self.dataset_fp = dataset_fp

    def get_prices(self, date):
        """
        Fetch prices for a given date

        Parameters
        ----------
        date : str
            Date to fetch prices for

        Returns
        -------
        list
            List of prices for the given date
        """
        # Load and process the data
        df = pd.read_csv(f"{self.dataset_fp}/price/raw/{self.ticker}.csv")
        df["Date"] = pd.to_datetime(df["Date"])
        df = df[df["Date"] == date]

        # Map rows to JSON
        prices_json = []
        for _, rows in df.iterrows():
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

    def get_news(self, date):
        """
        Fetch news for a given date

        Parameters
        ----------
        date : str
            Date to fetch news for

        Returns
        -------
        list
            List of news for the given date
        """
        # Load and process the data
        df = pd.read_csv(f"{self.dataset_fp}/news/raw/{self.ticker}.csv", sep="	")
        df["date"] = pd.to_datetime(df["date"])
        df = df[df["date"] == date]

        # Map rows to JSON
        news_json = []
        for _, rows in df.iterrows():
            news_json.append({"title": rows["title"], "summary": rows["summary"]})

        return news_json

# %%
# path = "/Users/odai/repos/cs-5588-team-gamestop/datasets/CMIN-US"
# date = "2018-01-02"

# aapl = MarketStock("AAPL", path)
# print(aapl.get_prices(date))
# print(aapl.get_news(date))

# %%
class Market:
    def __init__(self, dataset_fp):
        stocks = ['AAPL', 'JNJ', 'CVX', 'BAC', 'WMT'] # TODO: Make this dynamic
        self.stocks = {}
        for stock in stocks:
            self.stocks[stock] = MarketStock(stock, dataset_fp)
            
    def get_info(self, date):
        """
        Fetch information for all stocks for a given date
        
        Parameters
        ----------
        date : str
            Date to fetch information for
            
        Returns
        -------
        dict
            Dictionary containing information for the given date
        """
        stock_info = {}
        stat_df = self.get_stat_model_prediction(date)
        
        for ticker, stock in self.stocks.items():
            stock_info[ticker] = {
                "prices": stock.get_prices(date),
                "news": stock.get_news(date),
                "prediction": stat_df[stat_df["ticker"] == ticker][0]#.to_dict(orient="records")[0]
            }
        
        return stock_info
    
    def get_stat_model_prediction(self, date):
        path = "/Users/odai/repos/cs-5588-team-gamestop/datasets/stat-model-predictions-2021"
        return pd.read_csv(f"{path}/{date}.csv")

# %%
# date = "2018-01-02"
# path = "/Users/odai/repos/cs-5588-team-gamestop/datasets/CMIN-US"

# market = Market(path)
# print(json.dumps(market.get_info(date), indent=4))


