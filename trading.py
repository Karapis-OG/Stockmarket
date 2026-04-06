API_KEY = "YOUR_API_KEY_HERE"   # <-- insert your key later

watchlist = ["AAPL", "TSLA", "MSFT"]
portfolio_value = 10000

records = {}   # entry_price, shares_held, highest_price

def get_price(symbol):
    # placeholder for API call
    return 100.0

for symbol in watchlist:

    current_price = get_price(symbol)

    # initialize record
    if symbol not in records:
        records[symbol] = {
            "entry_price": 0,
            "shares_held": 0,
            "highest_price": 0
        }