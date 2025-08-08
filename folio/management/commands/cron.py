from django.core.management.base import BaseCommand
from django.db import models
import datetime, traceback, warnings, time, json

class Command(BaseCommand):
    warnings.filterwarnings("ignore")

    def handle(self, *args, **options):
        if 0 == 1: tasks()
        if 0 == 1: report()
        if 1 == 1: import_data()
        

######################################################################################################################
# TASK 
######################################################################################################################
def report():
    from folio.models import Account, Ticker, TradeTx
    account_name = "REER"
    account = Account.objects.get(name=account_name)
    symbols = list(set(TradeTx.objects.filter(account=account).values_list('ticker__symbol', flat=True)))
    total = 0
    for symbol in symbols:
        total_amount = TradeTx.objects.filter(account=account, ticker__symbol=symbol).aggregate(total=models.Sum('amount'))['total']
        total_qty = TradeTx.objects.filter(account=account, ticker__symbol=symbol).aggregate(total=models.Sum('qty'))['total']
        print(f"Symbol: {symbol}, Total Amount: {total_amount}, Total Qty: {total_qty}")
        if total_qty == 0: total += total_amount
    print(f"Total Amount for all symbols: {total}")


def import_data():
    from folio.models import Account, Ticker, TradeTx
    print(TradeTx.objects.filter(tx_type="DIVIDEND").update(price=0))

    if 1 == 1: return ######
    print("IMPORT DATA")
    with open('/app/data/db.json', 'r') as f:
        data = json.load(f)


    for ticker in list(data["ibkr_tx"].keys()):
        #print(f"{ticker}")
        if ticker in ["SPX"]: continue
        if Ticker.objects.filter(symbol=ticker).exists():
            print(f"{ticker} exists in Ticker model.")
        else:
            try: name = data["ibkr_tx"][ticker]["_content"]["transactions"][0]["desc"]
            except: name = ticker
            name = ''.join(word.capitalize() for word in name.split())
            Ticker.objects.create(symbol=ticker, currency='USD', name=name)
            print(f"Created new Ticker: {ticker}")
    
    if 1 == 1: return ######
    symbol = "NVDA"
    account_name = "REER"
    ticker = Ticker.objects.get(symbol=symbol)
    account = Account.objects.get(name=account_name)
    for item in data["ibkr_tx"][symbol]["_content"]["transactions"]:
        #print(item)
        try:
            date = datetime.datetime.strptime(item["date"], "%Y-%m-%d")
        except:
            date = datetime.datetime.strptime(item["date"], "%a %b %d %H:%M:%S %Z %Y")
        try:
            qty = item["qty"]
            price = item["pr"]
        except:
            qty = 0
            price = item["amt"]

        if qty == 0: tx_type = "DIVIDEND"
        if qty < 0: tx_type = "SELL"
        if qty > 0: tx_type = "BUY"

        print(date, tx_type, qty, price)
        tx = TradeTx.objects.create(
            date=date,
            account=account,
            ticker=ticker,
            tx_type=tx_type,
            qty=qty,
            price=price            
        )

    

def tasks():
    ### TICKER PRICE UPDATE
    print("--- UPDATE TICKER PRICE")
    from folio.models import Ticker
    from folio import api
    for ticker in Ticker.objects.all():
        #print(f"Ticker: {ticker.symbol} - {ticker.name} - {ticker.currency} - {ticker.price}")
        data = api.get_price(ticker.symbol, ticker.currency)
        if data["last"] is None:
            print(f"Ticker {ticker.symbol} not found or no price data available.")
            continue
        else:
            ticker.price = data["last"]
            ticker.save(update_fields=['price'])
            print(f"Updated Ticker: {ticker.symbol} - {ticker.name} - {ticker.currency} - {ticker.price}")
        time.sleep(1)