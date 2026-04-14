import requests
import time
API_KEY = "PKZMASPFSBXHBYJZPSPIZNL6ZF"   
API_SECRET = "CLDkrqXfLZmri4wotTKF6Dh9Zth7HFgErAzSGocn22Be"
BASE_URL = "https://app.alpaca.markets/dashboard/overview"




watchlist = ["AAPL", "TSLA", "MSFT"]
portfolio_value = 100000

# record structure:
# entry_price, shares_held, highest_price, last_trade_time
records = {}

def get_latest_price(symbol):
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        data = r.json()
        print(f"  [DEBUG] {symbol} raw response: {data}")  # remove once working
        return float(data["Global Quote"]["05. price"])
    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return 0.0

def check_cooldown(last_time, cooldown=60):
    return (time.time() - last_time) >= cooldown

print("Starting trading bot...\n")

while True:
    for symbol in watchlist:

        print(f"--- Checking {symbol} ---")
        current_price = get_latest_price(symbol)

        # initialize record
        if symbol not in records:
            records[symbol] = {
                "entry_price": 0,
                "shares_held": 0,
                "highest_price": 0,
                "last_trade_time": 0
            }

        entry_price = records[symbol]["entry_price"]
        shares_held = records[symbol]["shares_held"]
        highest_price = records[symbol]["highest_price"]

        # skip if price fetch failed
        if current_price == 0:
            print(f"  Skipping {symbol}, price unavailable.\n")
            continue

        # update highest price
        if shares_held > 0 and current_price > highest_price:
            records[symbol]["highest_price"] = current_price
            highest_price = current_price

        # compute profit %
        if shares_held > 0 and entry_price > 0:
            profit_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            profit_pct = 0

        # BUY logic — risk 10% of portfolio
        if shares_held == 0 and check_cooldown(records[symbol]["last_trade_time"]):
            risk_amount = portfolio_value * 0.10
            shares_to_buy = int(risk_amount / current_price)

            if shares_to_buy > 0:
                print(f"  BUY {shares_to_buy} shares of {symbol} at ${current_price:.2f}")
                records[symbol]["shares_held"] = shares_to_buy
                records[symbol]["entry_price"] = current_price
                records[symbol]["highest_price"] = current_price
                records[symbol]["last_trade_time"] = time.time()
            else:
                print(f"  Not enough budget to buy {symbol} at ${current_price:.2f}")

        # SELL logic — take profit at 2%
        elif shares_held > 0:
            if profit_pct >= 2.0:
                print(f"  SELL {shares_held} shares of {symbol} at ${current_price:.2f} | profit: {profit_pct:.4f}%")
                records[symbol]["shares_held"] = 0
                records[symbol]["entry_price"] = 0
                records[symbol]["highest_price"] = 0
                records[symbol]["last_trade_time"] = time.time()
            else:
                print(f"  HOLD {symbol} | current: ${current_price:.2f} | profit: {profit_pct:.4f}%")

        print()

    print("--- Cycle complete. Waiting 60 seconds... ---\n")
    time.sleep(60)