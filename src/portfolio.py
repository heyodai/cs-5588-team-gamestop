# %%
import json

# %%
class PortfolioStock:
    def __init__(self, ticker, value):
        self.ticker = ticker
        self.value = value
        self.amount = 0

    def buy(self, amount):
        self.amount += amount
        
    def sell(self, amount):
        self.amount -= amount
        
    def update(self, value):
        self.value = value

# %%
class Portfolio:
    def __init__(self):
        self.funds = 0  # Total available funds for buying stocks
        self.stocks = {}  # Dictionary to hold PortfolioStock objects for each ticker
    
    def add_funds(self, amount):
        """Adds funds to the portfolio."""
        self.funds += amount

    def buy_stock(self, ticker, amount, stock_value):
        """Buys a specified amount of stock if funds are sufficient."""
        total_cost = amount * stock_value
        if total_cost > self.funds:
            print("Insufficient funds.")
            return
        
        # Deduct funds
        self.funds -= total_cost
        
        # Add the stock to the portfolio or increase the amount if it already exists
        if ticker in self.stocks:
            self.stocks[ticker].buy(amount)
        else:
            stock = PortfolioStock(ticker, stock_value)
            stock.buy(amount)
            self.stocks[ticker] = stock

    def sell_stock(self, ticker, amount):
        """Sells a specified amount of stock if the stock is held in the portfolio."""
        if ticker not in self.stocks:
            print(f"No holdings in {ticker} to sell.")
            return
        stock = self.stocks[ticker]
        
        if amount > stock.amount:
            print("Insufficient shares to sell.")
            return
        
        # Calculate sale proceeds and update funds
        sale_proceeds = amount * stock.value
        self.funds += sale_proceeds
        stock.sell(amount)
        
        # Remove stock if no shares are left
        if stock.amount == 0:
            del self.stocks[ticker]

    def update_stock_value(self, ticker, new_value):
        """Updates the value of a specific stock."""
        if ticker in self.stocks:
            self.stocks[ticker].update(new_value)
        else:
            print(f"{ticker} is not in the portfolio.")
            
    def get_makeup(self):
        """Returns the portfolio's stock composition as a JSON string."""
        portfolio_data = {
            ticker: {"amount": stock.amount, "value": stock.value}
            for ticker, stock in self.stocks.items()
        }
        return json.dumps(portfolio_data, indent=2)
    
    def get_value(self):
        """Calculates the total value of the portfolio (cash + stocks)."""
        total_stock_value = sum(stock.amount * stock.value for stock in self.stocks.values())
        return self.funds + total_stock_value


# %%
# portfolio = Portfolio()
# portfolio.add_funds(1000)
# portfolio.buy_stock("AAPL", 10, 10)
# portfolio.buy_stock("GOOGL", 5, 1200)

# print(portfolio.get_makeup())


