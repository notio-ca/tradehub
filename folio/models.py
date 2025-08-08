from django.db import models
from django.db.models import Sum
from datetime import datetime

CURRENCY_CHOICES = [
    ('CAD', 'CAD'),
    ('USD', 'USD'),
]
TX_BUY = "BUY"
TX_SELL = "SELL"
TX_DIVIDEND = "DIVIDEND"
TX_TYPE_CHOICES = [
    (TX_BUY, 'Buy'),
    (TX_SELL, 'Sell'),
    (TX_DIVIDEND, 'Dividend'),
]

action_OPENED = "Opened"
action_AVG_DOWN = "Avg Down"
action_AVG_UP = "Avg Up"
action_TAKE_LOSS = "Take Loss"
action_TAKE_PROFIT = "Take Profit"
action_INCOME = "Income"

class Account(models.Model):
    name = models.CharField("Name", max_length=256, blank=False, default="")
    currency = models.CharField("Currency", max_length=3, choices=CURRENCY_CHOICES, default='CAD')
    data = models.JSONField("Data", blank=True, default=dict)

    investment = models.DecimalField("Investment", max_digits=10, decimal_places=2, blank=False, default=0, editable=False)
    #position = models.DecimalField("Position", max_digits=10, decimal_places=2, blank=False, default=0, editable=False)
    #balance = models.DecimalField("Balance", max_digits=10, decimal_places=2, blank=False, default=0, editable=False)
    
    def save(self, *args, **kwargs):
        self.investment = self.transactions.aggregate(total=Sum('amount'))['total'] or 0 #sum(tx.amount for tx in self.transactions.all())
        # symbols_list = list(set(self.trades.values_list('ticker__symbol', flat=True)))
        # position_open = 0
        # position_close = 0
        # print(symbols_list)
        # for symbol in symbols_list:
        #     total_amount = self.trades.filter(ticker__symbol=symbol).aggregate(total=models.Sum('amount'))['total']
        #     total_qty = self.trades.filter(ticker__symbol=symbol).aggregate(total=models.Sum('qty'))['total']
        #     print(f"Symbol: {symbol}, Total Amount: {total_amount}, Total Qty: {total_qty}")
        #     if total_qty == 0:
        #         position_close += total_amount
        #     else:
        #         position_open += total_amount

        # print(f"Position Open: {position_open}, Position Close: {position_close}")
        # self.position = -(self.trades.filter(tx_type__in=['BUY', 'SELL']).aggregate(total=Sum('amount'))['total'] or 0)
        # self.balance = self.investment - self.position
        super().save(*args, **kwargs)

    def new_tradefx(self, ticker):
        data = self.data
        if data.get('tickers', None) is None: data['tickers'] = {}
        if data['tickers'].get(ticker.id, None) is None:          
            data['tickers'][ticker.id] = {
                'symbol': ticker.symbol,
                'trade_list': []
            }
        data['tickers'][ticker.id]['symbol'] = ticker.symbol
        trade_list = []
        is_open = False
        for tradetx in self.trades.filter(ticker=ticker).order_by('date'):
            if not is_open:
                is_open = True
                trade_list.insert(0, {
                    'is_open': is_open,
                    'date_start': tradetx.date.isoformat(),
                    'date_end': None,
                    'date_days': None,
                    'qty': 0,
                    'avg': 0,
                    'even_avg': 0,
                    'cost': 0,
                    'balance': 0,
                    'dividend': 0,
                    'pnl': 0,
                    'tx':[]
                })
            trade = trade_list[0]

            last_qty = trade['qty']
            trade['qty'] += float(tradetx.qty)
            #last_cost = trade['cost']
            
            last_avg = trade['avg']

            pnl = 0
            pnl_pc = 0
            action = ""
            if tradetx.tx_type == TX_BUY:
                trade['cost'] += float(tradetx.amount)
                trade['balance'] += float(tradetx.amount)
                if trade['qty'] != 0:
                    trade['avg'] = abs(trade['cost']) / trade['qty']
                if last_qty == 0: action = action_OPENED
                elif last_avg >= trade['avg']: action = action_AVG_DOWN
                else: action = action_AVG_UP
            if tradetx.tx_type == TX_SELL:
                trade['cost'] += (abs(float(tradetx.qty)) * trade["avg"])
                trade['balance'] += float(tradetx.amount)
                pnl = (float(tradetx.price) - trade["avg"]) * abs(float(tradetx.qty))
                pnl_pc = (pnl / -(trade["avg"])) * 100
                trade['pnl'] += pnl
                if pnl >= 0: action = action_TAKE_PROFIT
                else: action = action_TAKE_LOSS
            if tradetx.tx_type == TX_DIVIDEND: 
                trade['cost'] += float(tradetx.amount)
                trade['avg'] = abs(trade['cost']) / trade['qty']
                action = action_INCOME
                trade['dividend'] += float(tradetx.amount)

            if trade['qty'] == 0: 
                is_open = False
                trade['is_open'] = is_open
                trade['date_end'] = tradetx.date.isoformat()
                trade['date_days'] = (datetime.fromisoformat(trade['date_end']) - datetime.fromisoformat(trade['date_start'])).days
            
            trade['tx'].append({
                'date': tradetx.date.isoformat(),
                'action': action,
                'tx_type': tradetx.tx_type,
                'qty': trade['qty'] if tradetx.tx_type == TX_DIVIDEND else float(tradetx.qty),
                'price': (float(tradetx.amount) / trade['qty']) if tradetx.tx_type == TX_DIVIDEND else float(tradetx.price),
                'amount': float(tradetx.amount),
                'pnl': pnl,
                'pnl_pc': pnl_pc,
                'pos_avg': trade['avg'],
                'pos_qty': trade['qty'],
                'pos_cost': trade['cost'],
            })  


        data['tickers'][ticker.id]['trade_list'] = trade_list
            #if
            # trade['date'] = trade['date'].isoformat()
            # #trade_list.append(dict(trade))
            # trade_list.append(trade)
            # continue
            # trade_list.append(f"{ticker.symbol} on {trade.date}: {trade.tx_type} {trade.qty} at {trade.price}")
            # print(f"{ticker.symbol} on {trade.date}: {trade.tx_type} {trade.qty} at {trade.price}")

        self.data = data
        self.save(update_fields=['data'])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = verbose_name

class AccountTx(models.Model):
    date = models.DateField("Date")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField("Balance", max_digits=10, decimal_places=2, blank=False)
    description = models.CharField("Description", max_length=256, blank=True, default="")

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.account.balance += self.amount
            self.account.save(update_fields=['balance'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account.name} - {self.amount} on {self.date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Account Tx"
        verbose_name_plural = verbose_name
        ordering = ['-date']

class Ticker(models.Model):
    symbol = models.CharField("Symbol", max_length=10, unique=True)
    name = models.CharField("Name", max_length=256, blank=False, default="")
    currency = models.CharField("Currency", max_length=3, choices=CURRENCY_CHOICES, default='CAD')
    price = models.DecimalField("Price", max_digits=10, decimal_places=2, blank=True, default=1.00)

    def __str__(self):
        return f"{self.symbol} - {self.currency} - {self.name}"

    class Meta:
        verbose_name = "Ticker"
        verbose_name_plural = verbose_name

class TradeTx(models.Model):
    date = models.DateTimeField("Date")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='trades')
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name='trades')
    tx_type = models.CharField("Type", max_length=18, choices=TX_TYPE_CHOICES, default='BUY')
    qty = models.DecimalField("Quantity", max_digits=10, decimal_places=2, blank=False)
    price = models.DecimalField("Price", max_digits=10, decimal_places=4, blank=False)
    # Computed field:
    amount = models.DecimalField("Amount", max_digits=10, decimal_places=2, blank=True, editable=False)

    def save(self, *args, **kwargs):
        self.qty = abs(self.qty)  # Ensure quantity is always positive
        if self.tx_type == 'BUY':
            self.amount = -(self.qty * self.price)
        elif self.tx_type == 'SELL':
            self.amount = self.qty * self.price
            self.qty = -(self.qty)
        elif self.tx_type == 'DIVIDEND':
            self.amount = self.price
            self.qty = 0
            self.price = 0
        super().save(*args, **kwargs)
        self.account.new_tradefx(self.ticker)


    def __str__(self):
        return f"{self.ticker.symbol} - {self.qty} at {self.price} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        verbose_name = "Trade Tx"
        verbose_name_plural = verbose_name
        ordering = ['-date']