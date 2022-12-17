from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import AddFileForm, RatiosAddForm
import xml.etree.ElementTree as ET
from .models import Document


class IndexView(View):
    def get(self, request):
        return render(request, "index.html")


class RatiosAdd(View):
    """Iterator for analyzing the company's financial result of manually entered data."""
    def get(self, request):
        form = RatiosAddForm()
        return render(request, 'ratios_manual_add_form.html', {'form': form})

    def post(self, request):
        form = RatiosAddForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data.get('company_name')
            number_nip = form.cleaned_data.get('number_NIP')
            number_nip = int(number_nip)
            year_result = form.cleaned_data.get('year_results')
            assets_fixed = form.cleaned_data.get('assets_fixed')
            assets_current = form.cleaned_data.get('assets_current')
            stock = form.cleaned_data.get('stock')
            receivables_short_term = form.cleaned_data.get('receivables_short_term')
            receivables_trade = form.cleaned_data.get('receivables_trade')
            receivables_tax = form.cleaned_data.get('receivables_tax')
            investments_short_term = form.cleaned_data.get('investments_short_term')
            assets_cash = form.cleaned_data.get('assets_cash')
            capital_share = form.cleaned_data.get('capital_share')
            provision_and_accruals = form.cleaned_data.get('provision_and_accruals')
            liabilities_long_therm = form.cleaned_data.get('liabilities_long_therm')
            liabilities_long_therm_financial = form.cleaned_data.get('liabilities_long_therm_financial')
            liabilities_short_therm = form.cleaned_data.get('liabilities_short_therm')
            liabilities_short_therm_financial = form.cleaned_data.get('liabilities_short_therm_financial')
            liabilities_trade = form.cleaned_data.get('liabilities_trade')
            revenue = form.cleaned_data.get('revenue')
            profit_operating = form.cleaned_data.get('profit_operating')
            depreciation = form.cleaned_data.get('depreciation')
            profit_gross = form.cleaned_data.get('profit_gross')
            tax_income = form.cleaned_data.get('tax_income')
            assets_total = assets_fixed + assets_current
            equity = assets_total - provision_and_accruals - liabilities_long_therm - liabilities_short_therm
            liabilities_and_equity = liabilities_long_therm + provision_and_accruals + equity + liabilities_short_therm
            profit_net = profit_gross - tax_income

            capitalization = round(equity / liabilities_and_equity * 100, 1)
            current_ratio = round(assets_current / liabilities_short_therm, 2)
            debt_ratio = round(liabilities_short_therm + liabilities_long_therm + provision_and_accruals, 0)
            debt_to_equity_ratio = round(debt_ratio / equity * 100, 1)
            receivables_turnover_ratio = round(receivables_trade / revenue * 360 * 1, 0)
            liabilities_turnover_ratio = round(liabilities_trade / revenue * 360 * 1, 0)
            profit_operating_margin = round(profit_operating / revenue * 100, 1)
            profit_net_margin = round(profit_net / revenue * 100, 1)
            debt_financial_net = round(liabilities_long_therm_financial + liabilities_short_therm_financial \
                                       - assets_cash, 0)
            ebitda = round(profit_operating + depreciation, 0)
            debt_financial_net_to_ebitda = round(debt_financial_net/ebitda, 2)


            if capitalization > 20 and current_ratio > 1 and debt_to_equity_ratio < 300:
                category = "Low risk"
            elif capitalization < 20 and current_ratio < 1 and debt_to_equity_ratio > 300 or debt_to_equity_ratio < 0:
                category = "High risk"
            else:
                category = "Medium risk"

        return render(request, 'ratios_detail.html', locals())


def convert_to_float(root, value):
    element = root.find(value)
    if element:
        element_value = element.find('.//{*}KwotaA').text
        element_value = round(float(element_value)/1000, 2)
    else:
        element_value = 0.00
    return element_value


def give_depreciation(root, value_first, value_second):
    depreciation = root.find(value_first)
    if depreciation:
        depreciation = depreciation.find('.//{*}KwotaA').text
        depreciation = round(float(depreciation) / 1000, 2)
    else:
        depreciation = root.find(value_second)
        depreciation = depreciation.find('.//{*}KwotaA').text
        depreciation = round(float(depreciation) / 1000, 2)
    return depreciation


class RatiosAddFile(View):
    """Iterator to analyze the financial result of the company automatically entered data."""

    def get(self, request):
        form = AddFileForm()
        return render(request, 'ratios_file_add.html', {'form': form})

    def post(self, request):
        form = AddFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = Document(file_name=request.FILES['file_name'])
            instance.save()

            tree = ET.parse(instance.file_name)
            root = tree.getroot()
            ET.register_namespace(""
                                  , "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaInnaWZlotych")

            element_year = root.find('.//{*}Naglowek')
            year = element_year.find('.//{*}OkresDo')
            year_result = year.text
            year_result = year_result[0:4]
            year_result = int(year_result)

            company_name = root.find('.//{*}NazwaFirmy')
            company_name = company_name.text

            number_nip = root.find('.//{*}P_1D')
            number_nip = number_nip.text
            number_nip = int(number_nip)

            company_pkd = root.find('.//{*}KodPKD')
            company_pkd = company_pkd.text

            assets_fixed = './/{*}Aktywa_A'
            assets_fixed = convert_to_float(root, assets_fixed)

            assets_current = './/{*}Aktywa_B'
            assets_current = convert_to_float(root, assets_current)

            element_assets_current = root.find('.//{*}Aktywa_B')
            stock = './/{*}Aktywa_B_I'
            stock = convert_to_float(element_assets_current, stock)

            receivables_short_term = './/{*}Aktywa_B_II'
            receivables_short_term = convert_to_float(root, receivables_short_term)

            receivables_trade_related = './/{*}Aktywa_B_II_1_A'
            receivables_trade_related = convert_to_float(root, receivables_trade_related)
            receivables_trade_shares = './/{*}Aktywa_B_II_2_A'
            receivables_trade_shares = convert_to_float(root, receivables_trade_shares)
            receivables_trade_other = './/{*}Aktywa_B_II_3_A'
            receivables_trade_other = convert_to_float(root, receivables_trade_other)
            receivables_trade = receivables_trade_related + receivables_trade_shares + receivables_trade_other

            receivables_tax = './/{*}Aktywa_B_II_3_B'
            receivables_tax = convert_to_float(root, receivables_tax)

            investments_short_term = './/{*}Aktywa_B_III'
            investments_short_term = convert_to_float(root, investments_short_term)

            assets_cash = './/{*}Aktywa_B_III_1_C'
            assets_cash = convert_to_float(root, assets_cash)

            equity = './/{*}Pasywa_A'
            equity = convert_to_float(root, equity)

            capital_share = './/{*}Pasywa_A_I'
            capital_share = convert_to_float(root, capital_share)

            provision = './/{*}Pasywa_B_I'
            provision = convert_to_float(root, provision)
            accruals = './/{*}Pasywa_B_IV'
            accruals = convert_to_float(root, accruals)
            provision_and_accruals = round(provision + accruals, 2)

            liabilities_long_therm = './/{*}Pasywa_B_II'
            liabilities_long_therm = convert_to_float(root, liabilities_long_therm)

            liabilities_long_therm_credits = './/{*}Pasywa_B_II_3_A'
            liabilities_long_therm_credits = convert_to_float(root, liabilities_long_therm_credits)
            liabilities_long_therm_other_financial = './/{*}Pasywa_B_II_3_C'
            liabilities_long_therm_other_financial = convert_to_float(root, liabilities_long_therm_other_financial)

            liabilities_long_therm_financial = liabilities_long_therm_credits + liabilities_long_therm_other_financial

            liabilities_short_therm = './/{*}Pasywa_B_III'
            liabilities_short_therm = convert_to_float(root, liabilities_short_therm)

            liabilities_short_therm_credits = './/{*}Pasywa_B_III_3_A'
            liabilities_short_therm_credits = convert_to_float(root, liabilities_short_therm_credits)
            liabilities_short_therm_other_financial = './/{*}Pasywa_B_III_3_C'
            liabilities_short_therm_other_financial = convert_to_float(root, liabilities_short_therm_other_financial)
            liabilities_short_therm_financial = liabilities_short_therm_credits+ liabilities_short_therm_other_financial

            liabilities_short_therm_trade_related = './/{*}Pasywa_B_III_1_A'
            liabilities_short_therm_trade_related = convert_to_float(root, liabilities_short_therm_trade_related)
            liabilities_short_therm_trade_shares = './/{*}Pasywa_B_III_2_A'
            liabilities_short_therm_trade_shares = convert_to_float(root, liabilities_short_therm_trade_shares)
            liabilities_short_therm_trade_other = './/{*}Pasywa_B_III_3_D_1'
            liabilities_short_therm_trade_other = convert_to_float(root, liabilities_short_therm_trade_other)
            liabilities_trade = liabilities_short_therm_trade_related + liabilities_short_therm_trade_shares \
                                + liabilities_short_therm_trade_other
            revenue = './/{*}A'
            revenue = convert_to_float(root, revenue)

            profit_operating = './/{*}F'
            profit_operating = convert_to_float(root, profit_operating)

            depreciation = give_depreciation(root, './/{*}B_I', './/{*}A_II_1')

            profit_gross = './/{*}I'
            profit_gross = convert_to_float(root, profit_gross)

            tax_income = './/{*}J'
            tax_income = convert_to_float(root, tax_income)

            profit_net = './/{*}L'
            profit_net = convert_to_float(root, profit_net)

            assets_total = './/{*}Aktywa'
            assets_total = convert_to_float(root, assets_total)

            liabilities_and_equity = './/{*}Pasywa'
            liabilities_and_equity = convert_to_float(root, liabilities_and_equity)

            capitalization = round(equity / liabilities_and_equity * 100, 1)
            current_ratio = round(assets_current / liabilities_short_therm, 2)
            debt_ratio = round(liabilities_short_therm + liabilities_long_therm + provision_and_accruals, 0)
            debt_to_equity_ratio = round(debt_ratio / equity * 100, 1)
            receivables_turnover_ratio = round(receivables_trade / revenue * 360 * 1, 0)
            liabilities_turnover_ratio = round(liabilities_trade / revenue * 360 * 1, 0)
            profit_operating_margin = round(profit_operating / revenue * 100, 1)
            profit_net_margin = round(profit_net / revenue * 100, 1)
            debt_financial_net = round(liabilities_long_therm_financial + liabilities_short_therm_financial \
                                   - assets_cash, 0)
            ebitda = round(profit_operating + depreciation, 0)
            debt_financial_net_to_ebitda = round(debt_financial_net / ebitda, 2)

            if capitalization > 20 and current_ratio > 1 and debt_to_equity_ratio < 300:
                category = "Low risk"
            elif capitalization < 20 and current_ratio < 1 and debt_to_equity_ratio > 300 or debt_to_equity_ratio < 0:
                category = "High risk"
            else:
                category = "Medium risk"

        return render(request, 'ratios_detail.html', locals())






