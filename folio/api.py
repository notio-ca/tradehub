import requests, json

# THOSE ARE FREE KEYS - SECURITY IS NOT A PRIORITY HERE
KEY_FINNHUB = "clp2ac9r01qn0q5tdicgclp2ac9r01qn0q5tdid0"
KEY_ALPHA = "9XV6S73D57DJ8MAV"
#KEY_ALPHA = "353C49FOZYVW9QMN"
#KEY_ALPHA = "QIIMRIRP206L7RPG"

def get_price(ticker, currency='USD'):
    try:
        data = { "ticker": "-", "last": None, "ask": "-", "bid": "-" }
        if currency == 'USD':
            r = requests.get(f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={KEY_FINNHUB}", verify=False)
            res = r.json()
            if 0 == 1: print(json.dumps(res, indent=4))
            if r.status_code == 200:
                data["ticker"] = ticker
                data["last"] = res["c"]
                return data
            
        elif currency == 'CAD':
            ticker = f"{ticker}.TO"
            r = requests.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={KEY_ALPHA}", verify=False)
            res = r.json()
            if 0 == 1: print(json.dumps(res, indent=4))
            if r.status_code == 200 and "Global Quote" in res:
                data["ticker"] = ticker
                data["last"] = float(res["Global Quote"]["05. price"])
                return data
    except:
        return data