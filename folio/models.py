from django.db import models

CURRENCY_CHOICES = [
    ('CAD', 'CAD'),
    ('USD', 'USD'),
]
TX_TYPE_CHOICES = [
    ('BUY', 'Buy'),
    ('SELL', 'Sell'),
    ('DIVIDEND', 'Dividend'),
]
class Account(models.Model):
    name = models.CharField("Name", max_length=256, blank=False, default="")
    investment = models.DecimalField("Investment", max_digits=10, decimal_places=2, blank=False, default=0, editable=False)
    position = models.DecimalField("Position", max_digits=10, decimal_places=2, blank=False, default=0, editable=False)
    balance = models.DecimalField("Balance", max_digits=10, decimal_places=2, blank=False, default=0, editable=False)
    currency = models.CharField("Currency", max_length=3, choices=CURRENCY_CHOICES, default='CAD')

    def calculate_balance(self):
        self.investment = sum(tx.amount for tx in self.transactions.all())
        self.position = sum(trade.amount for trade in self.trades.all())
        self.balance = self.investment + self.position
        self.save(update_fields=['balance', 'investment', 'position'])

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
    amount = models.DecimalField("Amount", max_digits=10, decimal_places=2, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if self.tx_type == 'BUY':
            self.amount = -(self.qty) * self.price
        elif self.tx_type == 'SELL':
            self.amount = self.qty * self.price
        elif self.tx_type == 'DIVIDEND':
            self.qty = 0
            self.amount = self.price
        super().save(*args, **kwargs)
        self.account.calculate_balance()


    def __str__(self):
        return f"{self.ticker.symbol} - {self.qty} at {self.price} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        verbose_name = "Trade Tx"
        verbose_name_plural = verbose_name
        ordering = ['-date']