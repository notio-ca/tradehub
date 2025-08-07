from django.contrib import admin, messages
from core.admin import ModelAdminBase, ModelInLineBase

from .models import *


@admin.register(Account)
class AccountAdmin(ModelAdminBase):
    list_display = []
    # search_fields = ["name"]

@admin.register(AccountTx)
class AccountTxAdmin(ModelAdminBase):
    list_display = []
    list_filter = ["account"]

@admin.register(Ticker)
class TickerAdmin(ModelAdminBase):
    list_display = []

@admin.register(TradeTx)
class TradeTxAdmin(ModelAdminBase):
    list_display = []
    list_filter = ["account", "ticker"]