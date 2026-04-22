import requests
import time
API_KEY = "PKW7CIYW3HKKYAKIMVR62KCYXX"   
API_SECRET = "82AHwTM2wvUD9RDsMGgCT5MqnFPz5nfHNK4uRAkux2y8"
BASE_URL = "https://paper-api.alpaca.markets/v2"

DATA_URL = "https://data.alpaca.markets/v2/stocks"
ORDER_URL = "https://paper-api.alpaca.markets/v2/orders"

watchlist = ["SNP", "TSLA", "MSFT"]
portfolio_value = 100000

records = {}


def get_latest_price(symbol):
    url = f"{DATA_URL}/{symbol}/quotes/latest"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        print(f"  [DEBUG] {symbol} raw response:", data)

        return float(data["quote"]["ap"])  # ask price

    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return 0.0


def place_order(symbol, qty, side):
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
        "Content-Type": "application/json"
    }

    order = {
        "symbol": symbol,
        "qty": qty,
        "side": side,       
        "type": "market",
        "time_in_force": "gtc"
    }

    try:
        r = requests.post(ORDER_URL, json=order, headers=headers)
        print("  [ORDER RESPONSE]", r.json())
    except Exception as e:
        print("  Order failed:", e)



def check_cooldown(last_time, cooldown=60):
    return (time.time() - last_time) >= cooldown



print("Starting trading bot...\n")

while True:
    for symbol in watchlist:

        print(f"--- Checking {symbol} ---")
        current_price = get_latest_price(symbol)

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

        if current_price == 0:
            print(f"  Skipping {symbol}, price unavailable.\n")
            continue

        if shares_held > 0 and current_price > highest_price:
            records[symbol]["highest_price"] = current_price
            highest_price = current_price

        if shares_held > 0 and entry_price > 0:
            profit_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            profit_pct = 0

       
        if shares_held == 0 and check_cooldown(records[symbol]["last_trade_time"]):
            risk_amount = portfolio_value * 0.10
            shares_to_buy = int(risk_amount / current_price)

            if shares_to_buy > 0:
                print(f"  BUY {shares_to_buy} shares of {symbol} at ${current_price:.2f}")
                place_order(symbol, shares_to_buy, "buy")  # REAL ORDER
                records[symbol]["shares_held"] = shares_to_buy
                records[symbol]["entry_price"] = current_price
                records[symbol]["highest_price"] = current_price
                records[symbol]["last_trade_time"] = time.time()
            else:
                print(f"  Not enough budget to buy {symbol} at ${current_price:.2f}")

    
        elif shares_held > 0:
            if profit_pct >= 2.0:
                print(f"  SELL {shares_held} shares of {symbol} at ${current_price:.2f} | profit: {profit_pct:.4f}%")
                place_order(symbol, shares_held, "sell")  # REAL ORDER
                records[symbol]["shares_held"] = 0
                records[symbol]["entry_price"] = 0
                records[symbol]["highest_price"] = 0
                records[symbol]["last_trade_time"] = time.time()
            else:
                print(f"  HOLD {symbol} | current: ${current_price:.2f} | profit: {profit_pct:.4f}%")

        print()

    print("--- Cycle complete. Waiting 60 seconds... ---\n")
    time.sleep(60)
