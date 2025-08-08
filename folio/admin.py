from django.contrib import admin, messages
from django import forms
from core.admin import ModelAdminBase, ModelInLineBase
from django_json_widget.widgets import JSONEditorWidget
from .models import *

class AccountForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['user'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

    class Meta:
        model = Account
        fields = ["name", "currency", "data"]
        widgets = {
            'data': JSONEditorWidget
        }

@admin.register(Account)
class AccountAdmin(ModelAdminBase):
    form = AccountForm
    list_display = ["edit", "name", "currency", "investment"]
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