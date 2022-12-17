from django import forms


class AddFileForm(forms.Form):
   file_name = forms.FileField()


class RatiosAddForm(forms.Form):
    company_name = forms.CharField(max_length=255)
    number_NIP = forms.IntegerField()
    year_results = forms.IntegerField()
    assets_fixed = forms.FloatField()
    assets_current = forms.FloatField()
    stock = forms.FloatField()
    receivables_short_term = forms.FloatField()
    receivables_trade = forms.FloatField()
    receivables_tax = forms.FloatField()
    investments_short_term = forms.FloatField()
    assets_cash = forms.FloatField()
    capital_share = forms.FloatField()
    provision_and_accruals = forms.FloatField()
    liabilities_long_therm = forms.FloatField()
    liabilities_long_therm_financial = forms.FloatField()
    liabilities_short_therm = forms.FloatField()
    liabilities_short_therm_financial = forms.FloatField()
    liabilities_trade = forms.FloatField()
    revenue = forms.FloatField()
    profit_operating = forms.FloatField()
    depreciation = forms.FloatField()
    profit_gross = forms.FloatField()
    tax_income = forms.FloatField()


















