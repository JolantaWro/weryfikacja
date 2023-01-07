from django.shortcuts import render, redirect
from django.views import View
from .forms import AddFileForm, RatiosAddForm
import xml.etree.ElementTree as ET
from .models import Document


class IndexView(View):
   def get(self, request):
       return render(request, "index.html")


class RatiosAdd(View):
   """Iterator for analyzing the company's financial result."""
   def get(self, request):
       form = RatiosAddForm()
       return render(request, 'ratios_manual_add_form.html', {'form': form})

   def post(self, request):
       form = RatiosAddForm(request.POST)
       if form.is_valid():
           company_name = form.cleaned_data.get('nazwa_firmy')
           number_nip = form.cleaned_data.get('numer_NIP')
           number_nip = int(number_nip)
           year_result = form.cleaned_data.get('rok')
           assets_fixed = form.cleaned_data.get('aktywa_trwałe')
           assets_current = form.cleaned_data.get('aktywa_obrotowe')
           stock = form.cleaned_data.get('zapasy')
           receivables_short_term = form.cleaned_data.get('należności_krótkoterminowe')
           receivables_trade = form.cleaned_data.get('należności_handlowe')
           receivables_tax = form.cleaned_data.get('należności_podatkowe')
           investments_short_term = form.cleaned_data.get('inwestycje_krótkoterminowe')
           assets_cash = form.cleaned_data.get('środki_pieniężne')
           capital_share = form.cleaned_data.get('kapitał_podstawowy')
           provision_and_accruals = form.cleaned_data.get('rezerwy_i_rozliczenia_międzyokresowe')
           liabilities_long_therm = form.cleaned_data.get('zobowiązania_długoterminowe')
           liabilities_long_therm_financial = form.cleaned_data.get('zobowiązania_długoterminowe_finansowe')
           liabilities_short_therm = form.cleaned_data.get('zobowiązania_krótkoterminowe')
           liabilities_short_therm_financial = form.cleaned_data.get('zobowiązania_krótkoterminowe_finansowe')
           liabilities_trade = form.cleaned_data.get('zobowiązania_handlowe')
           revenue = form.cleaned_data.get('przychody')
           profit_operating = form.cleaned_data.get('wynik_z_działalności_operacyjnej')
           depreciation = form.cleaned_data.get('amortyzacja')
           profit_gross = form.cleaned_data.get('wynik_brutto')
           tax_income = form.cleaned_data.get('podatek_dochodowy')
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
               category = "Niskie ryzyko"
           elif capitalization < 20 and current_ratio < 1 and debt_to_equity_ratio > 300 or debt_to_equity_ratio < 0:
               category = "Wysokie ryzyko"
           else:
               category = "Średnie ryzyko, zwróć uwagę na poziom kapitalizacji, płynności oraz zadłużenia"

       return render(request, 'ratios_detail.html', locals())


def convert_to_float(root, value):
   element = root.find(value)
   if element:
       element_value = element.find('.//{*}KwotaA').text
       # element_value = round(float(element_value)/1000, 2)
       element_value = round(float(element_value), 2)
   else:
       element_value = 0.00
   return element_value

def convert_to_float_value_before(root, value):
  element = root.find(value)
  if element:
      element_value = element.find('.//{*}KwotaB').text
      element_value = round(float(element_value), 2)
  else:
      element_value = 0.00
  return element_value




def give_depreciation(root, value_first, value_second):
   depreciation = root.find(value_first)
   if depreciation:
       depreciation = depreciation.find('.//{*}KwotaA').text
       # depreciation = round(float(depreciation) / 1000, 2)
       depreciation = round(float(depreciation), 2)
   else:
       depreciation = root.find(value_second)
       depreciation = depreciation.find('.//{*}KwotaA').text
       # depreciation = round(float(depreciation) / 1000, 2)
       depreciation = round(float(depreciation), 2)
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
           # instance.save()

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

           assets_fixed_before = './/{*}Aktywa_B'
           assets_fixed_before = convert_to_float(root, assets_fixed_before)

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
               category = "Niskie ryzyko"
           elif capitalization < 20 and current_ratio < 1 and debt_to_equity_ratio > 300 or debt_to_equity_ratio < 0:
               category = "Wysokie ryzyko"
           else:
               category = "Średnie ryzyko, zwróć uwagę na poziom kapitalizacji, płynności oraz zadłużenia"

       return redirect('ratios_edit', company_name=company_name, number_nip=number_nip, year_result=year_result
                       , assets_fixed=assets_fixed, assets_current=assets_current, stock=stock
                       , receivables_short_term=receivables_short_term, receivables_trade=receivables_trade
                       , receivables_tax=receivables_tax, investments_short_term=investments_short_term
                       , assets_cash=assets_cash, capital_share=capital_share, provision_and_accruals=provision_and_accruals
                       , liabilities_long_therm=liabilities_long_therm, liabilities_long_therm_financial=liabilities_long_therm_financial
                       , liabilities_short_therm=liabilities_short_therm, liabilities_short_therm_financial=liabilities_short_therm_financial
                       , liabilities_trade=liabilities_trade, revenue=revenue, profit_operating=profit_operating
                       , depreciation=depreciation, profit_gross=profit_gross, tax_income=tax_income)

class RatiosEdit(View):
   """Iterator for analyzing the company's financial result of manually edit data."""
   def get(self, request, company_name, number_nip, year_result, assets_fixed, assets_current, stock
           , receivables_short_term, receivables_trade, receivables_tax, investments_short_term, assets_cash
           , capital_share, provision_and_accruals, liabilities_long_therm, liabilities_long_therm_financial
           , liabilities_short_therm, liabilities_short_therm_financial, liabilities_trade, revenue
           , profit_operating, depreciation, profit_gross, tax_income):
       form = RatiosAddForm(initial={'nazwa_firmy': company_name, 'numer_NIP': number_nip, 'rok': year_result
                       , 'aktywa_trwałe': assets_fixed, 'aktywa_obrotowe': assets_current, 'zapasy': stock
                       , 'należności_krótkoterminowe': receivables_short_term, 'należności_handlowe': receivables_trade
                       , 'należności_podatkowe': receivables_tax, 'inwestycje_krótkoterminowe': investments_short_term
                       , 'środki_pieniężne': assets_cash, 'kapitał_podstawowy': capital_share
                       , 'rezerwy_i_rozliczenia_międzyokresowe': provision_and_accruals, 'zobowiązania_długoterminowe': liabilities_long_therm
           , 'zobowiązania_długoterminowe_finansowe': liabilities_long_therm_financial, 'zobowiązania_krótkoterminowe': liabilities_short_therm
           , 'zobowiązania_krótkoterminowe_finansowe': liabilities_short_therm_financial, 'zobowiązania_handlowe': liabilities_trade
           , 'przychody': revenue, 'wynik_z_działalności_operacyjnej': profit_operating, 'amortyzacja': depreciation
           , 'wynik_brutto': profit_gross, 'podatek_dochodowy': tax_income})
       return render(request, 'ratios_manual_add_form.html', {'form': form, 'nazwa_firmy': company_name, 'numer_NIP': number_nip
       ,'rok': year_result, 'aktywa_trwałe': assets_fixed, 'aktywa_obrotowe': assets_current, 'zapasy': stock
       , 'należności_krótkoterminowe': receivables_short_term, 'należności_handlowe': receivables_trade
       , 'należności_podatkowe': receivables_tax, 'inwestycje_krótkoterminowe': investments_short_term
       , 'środki_pieniężne': assets_cash, 'kapitał_podstawowy': capital_share, 'rezerwy_i_rozliczenia_międzyokresowe': provision_and_accruals
       , 'zobowiązania_długoterminowe': liabilities_long_therm, 'zobowiązania_długoterminowe_finansowe': liabilities_long_therm_financial
       , 'zobowiązania_krótkoterminowe': liabilities_short_therm, 'zobowiązania_krótkoterminowe_finansowe': liabilities_short_therm_financial
       , 'zobowiązania_handlowe': liabilities_trade, 'przychody': revenue, 'wynik_z_działalności_operacyjnej': profit_operating
       , 'amortyzacja': depreciation, 'wynik_brutto': profit_gross, 'podatek_dochodowy': tax_income})

   def post(self, request, company_name, number_nip, year_result, assets_fixed, assets_current, stock
           , receivables_short_term, receivables_trade, receivables_tax, investments_short_term, assets_cash
           , capital_share, provision_and_accruals, liabilities_long_therm, liabilities_long_therm_financial
           , liabilities_short_therm, liabilities_short_therm_financial, liabilities_trade, revenue
           , profit_operating, depreciation, profit_gross, tax_income):
       form = RatiosAddForm(request.POST)
       if form.is_valid():
           company_name = form.cleaned_data.get('nazwa_firmy')
           number_nip = form.cleaned_data.get('numer_NIP')
           number_nip = int(number_nip)
           year_result = form.cleaned_data.get('rok')
           assets_fixed = form.cleaned_data.get('aktywa_trwałe')
           assets_current = form.cleaned_data.get('aktywa_obrotowe')
           stock = form.cleaned_data.get('zapasy')
           receivables_short_term = form.cleaned_data.get('należności_krótkoterminowe')
           receivables_trade = form.cleaned_data.get('należności_handlowe')
           receivables_tax = form.cleaned_data.get('należności_podatkowe')
           investments_short_term = form.cleaned_data.get('inwestycje_krótkoterminowe')
           assets_cash = form.cleaned_data.get('środki_pieniężne')
           capital_share = form.cleaned_data.get('kapitał_podstawowy')
           provision_and_accruals = form.cleaned_data.get('rezerwy_i_rozliczenia_międzyokresowe')
           liabilities_long_therm = form.cleaned_data.get('zobowiązania_długoterminowe')
           liabilities_long_therm_financial = form.cleaned_data.get('zobowiązania_długoterminowe_finansowe')
           liabilities_short_therm = form.cleaned_data.get('zobowiązania_krótkoterminowe')
           liabilities_short_therm_financial = form.cleaned_data.get('zobowiązania_krótkoterminowe_finansowe')
           liabilities_trade = form.cleaned_data.get('zobowiązania_handlowe')
           revenue = form.cleaned_data.get('przychody')
           profit_operating = form.cleaned_data.get('wynik_z_działalności_operacyjnej')
           depreciation = form.cleaned_data.get('amortyzacja')
           depreciation = float(depreciation)
           profit_gross = form.cleaned_data.get('wynik_brutto')
           tax_income = form.cleaned_data.get('podatek_dochodowy')
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
               category = "Niskie ryzyko"
           elif capitalization < 20 and current_ratio < 1 and debt_to_equity_ratio > 300 or debt_to_equity_ratio < 0:
               category = "Wysokie ryzyko"
           else:
               category = "Średnie ryzyko, zwróć uwagę na poziom kapitalizacji, płynności oraz zadłużenia"

       return render(request, 'ratios_detail.html', locals())

class RatiosViewFile(View):
   """Iterator to analyze the financial result of the company automatically entered data."""

   def get(self, request):
       form = AddFileForm()
       return render(request, 'ratios_file_add.html', {'form': form})

   def post(self, request):
       form = AddFileForm(request.POST, request.FILES)
       if form.is_valid():
           instance = Document(file_name=request.FILES['file_name'])
           # instance.save()

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
               category = "Niskie ryzyko"
           elif capitalization < 20 and current_ratio < 1 and debt_to_equity_ratio > 300 or debt_to_equity_ratio < 0:
               category = "Wysokie ryzyko"
           else:
               category = "Średnie ryzyko, zwróć uwagę na poziom kapitalizacji, płynności oraz zadłużenia"

       return render(request, 'ratios_detail.html', locals())



class FileDetail(View):
   """View element od file analize"""

   def get(self, request):
       form = AddFileForm()
       return render(request, 'ratios_file_add.html', {'form': form})

   def post(self, request):
       form = AddFileForm(request.POST, request.FILES)
       if form.is_valid():
           instance = Document(file_name=request.FILES['file_name'])
           # instance.save()

           tree = ET.parse(instance.file_name)
           root = tree.getroot()
           ET.register_namespace(""
                                 , "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaInnaWZlotych")

           element_year = root.find('.//{*}Naglowek')
           year = element_year.find('.//{*}OkresDo')
           year_result = year.text

           year_before = element_year.find('.//{*}OkresOd')
           year_before = year_before.text

           report_date = element_year.find('.//{*}DataSporzadzenia')
           report_date = report_date.text

           report_code = element_year.find('.//{*}KodSprawozdania')
           report_code = report_code.text

           code_balance = root.find('.//{*}Bilans')
           if code_balance is not None:
               balance = f"Bilans"

           code_profit_loss_account = root.find('.//{*}RZiS')
           if code_profit_loss_account is not None:
               profit_loss_account = f"Rachunek zysków i strat"

           code_capital_changes = root.find('.//{*}ZestZmianWKapitale')
           if code_capital_changes is not None:
               capital_changes = f"Zestawienie zmian w kapitale (funduszu) własnym"

           code_cash_flow = root.find('.//{*}RachPrzeplywow')
           if code_cash_flow is not None:
               code_cash_flow = f"Rachunek przepływów pieniężnych"

           code_report = root.find('.//{*}RZiSKalk')
           if code_report is not None:
               message = f"Wariant kalkulacyjny"

           code_cash_flow = root.find('.//{*}PrzeplywyPosr')
           if code_report is not None:
               intermediate = f"Metoda pośrednia"

           company_name = root.find('.//{*}NazwaFirmy')
           company_name = company_name.text

           company_address = root.find('.//{*}Adres')
           company_address_city = company_address.find('.//{*}Miejscowosc')
           company_address_city = company_address_city.text
           company_address_street = company_address.find('.//{*}Ulica')
           company_address_street = company_address_street.text
           company_address_street_number = company_address.find('.//{*}NrDomu')
           company_address_street_number = company_address_street_number.text
           company_address_post_code = company_address.find('.//{*}KodPocztowy')
           company_address_post_code = company_address_post_code.text

           number_nip = root.find('.//{*}P_1D')
           number_nip = number_nip.text
           number_nip = int(number_nip)

           company_pkd = root.find('.//{*}KodPKD')
           company_pkd = company_pkd.text

           company_krs = root.find('.//{*}P_1E')
           company_krs = company_krs.text

           report_date_start = root.find('.//{*}DataOd')
           report_date_start = report_date_start.text

           report_date_finish = root.find('.//{*}DataDo')
           report_date_finish = report_date_finish.text

           report_joint = root.find('.//{*}P_4')
           report_joint = report_joint.text

           report_continuing_future = root.find('.//{*}P_5A')
           report_continuing_future = report_continuing_future.text

           report_continuing_denger = root.find('.//{*}P_5B')
           report_continuing_denger = report_continuing_denger.text

           assets_fixed = convert_to_float(root, './/{*}Aktywa_A')
           assets_fixed_before = convert_to_float_value_before(root, './/{*}Aktywa_A')

           assets_fixed_intangible = convert_to_float(root, './/{*}Aktywa_A_I')
           assets_fixed_intangible_before = convert_to_float_value_before(root, './/{*}Aktywa_A_I')

           research_and_development = convert_to_float(root, './/{*}Aktywa_A_I_1')
           research_and_development_before = convert_to_float_value_before(root, './/{*}Aktywa_A_I_1')

           goodwill = convert_to_float(root, './/{*}Aktywa_A_I_2')
           goodwill_before = convert_to_float_value_before(root, './/{*}Aktywa_A_I_2')

           assets_fixed_intangible_other = convert_to_float(root, './/{*}Aktywa_A_I_3')
           assets_fixed_intangible_other_before = convert_to_float_value_before(root, './/{*}Aktywa_A_I_3')

           advances_for_assets_fixed_intangible = convert_to_float(root, './/{*}Aktywa_A_I_4')
           advances_for_assets_fixed_intangible_before = convert_to_float_value_before(root, './/{*}Aktywa_A_I_4')

           tangible_fixed_assets = convert_to_float(root, './/{*}Aktywa_A_II')
           tangible_fixed_assets_before = convert_to_float_value_before(root, './/{*}Aktywa_A_II')

           assets_fixed_assets_fixed = convert_to_float(root, './/{*}Aktywa_A_II_1')
           assets_fixed_assets_fixed_before = convert_to_float_value_before(root, './/{*}Aktywa_A_II_1')

           freehold_land = convert_to_float(root, './/{*}Aktywa_A_II_1_A')
           freehold_land_before = convert_to_float_value_before(root, './/{*}Aktywa_A_II_1_A')

           buildings_and_constructions = convert_to_float(root, './/{*}Aktywa_A_II_1_B')
           buildings_and_constructions_before = convert_to_float_value_before(root, './/{*}Aktywa_A_II_1_B')

           plant_and_equipment = convert_to_float(root, './/{*}Aktywa_A_II_1_C')
           plant_and_equipment_before = convert_to_float_value_before(root, './/{*}Aktywa_A_II_1_C')

           vehicles = convert_to_float(root, './/{*}Aktywa_A_II_1_D')
           vehicles_before = convert_to_float_value_before(root, './/{*}Aktywa_A_II_1_D')

           assets_fixed_assets_fixed_other = convert_to_float(root, './/{*}Aktywa_A_II_1_E')
           assets_fixed_assets_fixed_other_before = convert_to_float_value_before(root, './/{*}Aktywa_A_II_1_E')

           assets_under_construction = convert_to_float(root, './/{*}Aktywa_A_II_2')
           assets_under_construction_before = convert_to_float_value_before(root, './/{*}Aktywa_A_II_2')

           advances_for_assets_under_construction = convert_to_float(root, './/{*}Aktywa_A_II_3')
           advances_for_assets_under_construction_before = convert_to_float_value_before(root, './/{*}Aktywa_A_II_3')

           receivables_long_term = convert_to_float(root, './/{*}Aktywa_A_III')
           receivables_long_term_before = convert_to_float_value_before(root, './/{*}Aktywa_A_III')

           receivables_long_term_related = convert_to_float(root, './/{*}Aktywa_A_III_1')
           receivables_long_term_related_before = convert_to_float_value_before(root, './/{*}Aktywa_A_III_1')

           receivables_long_term_shares = convert_to_float(root, './/{*}Aktywa_A_III_2')
           receivables_long_term_shares_before = convert_to_float_value_before(root, './/{*}Aktywa_A_III_2')

           receivables_long_term_other = convert_to_float(root, './/{*}Aktywa_A_III_3')
           receivables_long_term_other_before = convert_to_float_value_before(root, './/{*}Aktywa_A_III_3')

           investments_long_term = convert_to_float(root, './/{*}Aktywa_A_IV')
           investments_long_term_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV')

           real_estate = convert_to_float(root, './/{*}Aktywa_A_IV_1')
           real_estate_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_1')

           investments_assets_fixed_intangible = convert_to_float(root, './/{*}Aktywa_A_IV_2')
           investments_assets_fixed_intangible_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_2')
           assets_financial_long_term = convert_to_float(root, './/{*}Aktywa_A_IV_3')
           assets_financial_long_term_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3')

           assets_financial_long_term_related = convert_to_float(root, './/{*}Aktywa_A_IV_3_A')
           assets_financial_long_term_related_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_A')

           assets_financial_long_term_related_shares_or_stocks = convert_to_float(root, './/{*}Aktywa_A_IV_3_A_1')
           assets_financial_long_term_related_shares_or_stocks_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_A_1')

           assets_financial_long_term_related_other_securities = convert_to_float(root, './/{*}Aktywa_A_IV_3_A_2')
           assets_financial_long_term_related_other_securities_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_A_2')

           assets_financial_long_term_related_loans_granted = convert_to_float(root, './/{*}Aktywa_A_IV_3_A_3')
           assets_financial_long_term_related_loans_granted_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_A_3')

           assets_financial_long_term_related_other = convert_to_float(root, './/{*}Aktywa_A_IV_3_A_4')
           assets_financial_long_term_related_other_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_A_4')

           assets_financial_long_term_shares = convert_to_float(root, './/{*}Aktywa_A_IV_3_B')
           assets_financial_long_term_shares_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_B')

           assets_financial_long_term_shares_shares_or_stocks = convert_to_float(root, './/{*}Aktywa_A_IV_3_B_1')
           assets_financial_long_term_shares_shares_or_stocks_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_B_1')

           assets_financial_long_term_shares_other_securities = convert_to_float(root, './/{*}Aktywa_A_IV_3_B_2')
           assets_financial_long_term_shares_other_securities_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_B_2')

           assets_financial_long_term_shares_loans_granted = convert_to_float(root, './/{*}Aktywa_A_IV_3_B_3')
           assets_financial_long_term_shares_loans_granted_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_B_3')

           assets_financial_long_term_shares_other = convert_to_float(root, './/{*}Aktywa_A_IV_3_B_4')
           assets_financial_long_term_shares_other_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_B_4')

           assets_financial_long_term_other = convert_to_float(root, './/{*}Aktywa_A_IV_3_C')
           assets_financial_long_term_other_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_C')

           assets_financial_long_term_other_shares_or_stocks = convert_to_float(root, './/{*}Aktywa_A_IV_3_C_1')
           assets_financial_long_term_other_shares_or_stocks_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_C_1')

           assets_financial_long_term_other_other_securities = convert_to_float(root, './/{*}Aktywa_A_IV_3_C_2')
           assets_financial_long_term_other_other_securities_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_C_2')

           assets_financial_long_term_other_loans_granted = convert_to_float(root, './/{*}Aktywa_A_IV_3_C_3')
           assets_financial_long_term_other_loans_granted_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_C_3')

           assets_financial_long_term_other_other = convert_to_float(root, './/{*}Aktywa_A_IV_3_C_4')
           assets_financial_long_term_other_other_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_3_C_4')

           assets_financial_long_term_other_assets_financial_other = convert_to_float(root, './/{*}Aktywa_A_IV_4')
           assets_financial_long_term_other_assets_financial_other_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV_4')

           prepayments_long_term = convert_to_float(root, './/{*}Aktywa_A_V')
           prepayments_long_term_before = convert_to_float_value_before(root, './/{*}Aktywa_A_V')

           deferred_tax_assets = convert_to_float(root, './/{*}Aktywa_A_V_1')
           deferred_tax_assets_before = convert_to_float_value_before(root, './/{*}Aktywa_A_V_1')

           prepayments_other = convert_to_float(root, './/{*}Aktywa_A_V_2')
           prepayments_other_before = convert_to_float_value_before(root, './/{*}Aktywa_A_V_2')

           assets_current = convert_to_float(root, './/{*}Aktywa_B')
           assets_current_before = convert_to_float_value_before(root,  './/{*}Aktywa_B')

           stock = convert_to_float(root, './/{*}Aktywa_B_I')
           stock_before = convert_to_float_value_before(root, './/{*}Aktywa_B_I')

           raw_materials = convert_to_float(root, './/{*}Aktywa_B_I_1')
           raw_materials_before = convert_to_float_value_before(root, './/{*}Aktywa_B_I_1')

           semi_finished_products = convert_to_float(root, './/{*}Aktywa_B_I_2')
           semi_finished_products_before = convert_to_float_value_before(root, './/{*}Aktywa_B_I_2')

           finished_products = convert_to_float(root, './/{*}Aktywa_B_I_3')
           finished_products_before = convert_to_float_value_before(root, './/{*}Aktywa_B_I_3')

           goods_for_resale = convert_to_float(root, './/{*}Aktywa_B_I_4')
           goods_for_resale_before = convert_to_float_value_before(root, './/{*}Aktywa_B_I_4')

           advances_for_deliveries = convert_to_float(root, './/{*}Aktywa_B_I_5')
           advances_for_deliveries_before = convert_to_float_value_before(root, './/{*}Aktywa_B_I_5')

           receivables_short_term = convert_to_float(root, './/{*}Aktywa_B_II')
           receivables_short_term_before = convert_to_float_value_before(root, './/{*}Aktywa_B_II')

           receivables_short_term_related = convert_to_float(root, './/{*}Aktywa_B_II_1')
           receivables_short_term_related_before = convert_to_float_value_before(root, './/{*}Aktywa_B_II_1')
           receivables_short_term_related_trade_due_dates = convert_to_float(root, './/{*}Aktywa_B_II_1_A')
           receivables_short_term_related_trade_due_dates_before = convert_to_float_value_before(root, './/{*}Aktywa_B_II_1_A')
           receivables_short_term_related_trade_within_12 = convert_to_float(root, './/{*}Aktywa_B_II_1_A_1')
           receivables_short_term_related_trade_within_12_before = convert_to_float_value_before(root,
                                                                                                 './/{*}Aktywa_B_II_1_A_1')
           receivables_short_term_related_trade_more_12 = convert_to_float(root, './/{*}Aktywa_B_II_1_A_2')
           receivables_short_term_related_trade_more_12_before = convert_to_float_value_before(root,
                                                                                                 './/{*}Aktywa_B_II_1_A_2')
           receivables_short_term_related_other = convert_to_float(root, './/{*}Aktywa_B_II_1_B')
           receivables_short_term_related_other_before = convert_to_float_value_before(root,
                                                                                               './/{*}Aktywa_B_II_1_B')

           receivables_short_term_shares = convert_to_float(root, './/{*}Aktywa_B_II_2')
           receivables_short_term_shares_before = convert_to_float_value_before(root, './/{*}Aktywa_B_II_2')
           receivables_short_term_shares_trade_due_dates = convert_to_float(root, './/{*}Aktywa_B_II_2_A')
           receivables_short_term_shares_trade_due_dates_before = convert_to_float_value_before(root,
                                                                                         './/{*}Aktywa_B_II_2_A')
           receivables_short_term_shares_trade_within_12 = convert_to_float(root, './/{*}Aktywa_B_II_2_A_1')
           receivables_short_term_shares_trade_within_12_before = convert_to_float_value_before(root,
                                                                                          './/{*}Aktywa_B_II_2_A_1')
           receivables_short_term_shares_trade_more_12 = convert_to_float(root, './/{*}Aktywa_B_II_2_A_2')
           receivables_short_term_shares_trade_more_12_before = convert_to_float_value_before(root,
                                                                                        './/{*}Aktywa_B_II_2_A_2')
           receivables_short_term_shares_other = convert_to_float(root, './/{*}Aktywa_B_II_2_B')
           receivables_short_term_shares_other_before = convert_to_float_value_before(root,
                                                                                       './/{*}Aktywa_B_II_2_B')

           receivables_short_term_other = convert_to_float(root, './/{*}Aktywa_B_II_3')
           receivables_short_term_other_before = convert_to_float_value_before(root, './/{*}Aktywa_B_II_3')
           receivables_short_term_other_trade_due_dates = convert_to_float(root, './/{*}Aktywa_B_II_3_A')
           receivables_short_term_other_trade_due_dates_before = convert_to_float_value_before(root,
                                                                                          './/{*}Aktywa_B_II_3_A')
           receivables_short_term_other_trade_within_12 = convert_to_float(root, './/{*}Aktywa_B_II_3_A_1')
           receivables_short_term_other_trade_within_12_before = convert_to_float_value_before(root,
                                                                                          './/{*}Aktywa_B_II_3_A_1')
           receivables_short_term_other_trade_more_12 = convert_to_float(root, './/{*}Aktywa_B_II_3_A_2')
           receivables_short_term_other_trade_more_12_before = convert_to_float_value_before(root,
                                                                                        './/{*}Aktywa_B_II_3_A_2')
           receivables_short_term_other_tax = convert_to_float(root, './/{*}Aktywa_B_II_3_B')
           receivables_short_term_other_tax_before = convert_to_float_value_before(root,
                                                                                      './/{*}Aktywa_B_II_3_B')
           receivables_short_term_other_other = convert_to_float(root, './/{*}Aktywa_B_II_3_C')
           receivables_short_term_other_other_before = convert_to_float_value_before(root,
                                                                                   './/{*}Aktywa_B_II_3_C')

           receivables_short_term_other_in_court = convert_to_float(root, './/{*}Aktywa_B_II_3_D')
           receivables_short_term_other_in_court_before = convert_to_float_value_before(root,
                                                                                     './/{*}Aktywa_B_II_3_D')

           investments_short_term = convert_to_float(root, './/{*}Aktywa_B_III')
           investments_short_term_before = convert_to_float_value_before(root, './/{*}Aktywa_B_III')

           assets_financial_short_term = convert_to_float(root, './/{*}Aktywa_B_III_1')
           assets_financial_short_term_before = convert_to_float_value_before(root, './/{*}Aktywa_B_III_1')
           assets_financial_short_term_related = convert_to_float(root, './/{*}Aktywa_B_III_1_A')
           assets_financial_short_term_related_before = convert_to_float_value_before(root, './/{*}Aktywa_B_III_1_A')
           assets_financial_short_term_related_shares_or_stocks = convert_to_float(root, './/{*}Aktywa_B_III_1_A_1')
           assets_financial_short_term_related_shares_or_stocks_before = convert_to_float_value_before(root,
                                                                                                  './/{*}Aktywa_B_III_1_A_1')
           assets_financial_short_term_related_other_securities = convert_to_float(root, './/{*}Aktywa_B_III_1_A_2')
           assets_financial_short_term_related_other_securities_before = convert_to_float_value_before(root,
                                                                                                  './/{*}Aktywa_B_III_1_A_2')
           assets_financial_short_term_related_loans_granted = convert_to_float(root, './/{*}Aktywa_B_III_1_A_3')
           assets_financial_short_term_related_loans_granted_before = convert_to_float_value_before(root,
                                                                                               './/{*}Aktywa_B_III_1_A_3')
           assets_financial_short_term_related_other = convert_to_float(root, './/{*}Aktywa_B_III_1_A_4')
           assets_financial_short_term_related_other_before = convert_to_float_value_before(root,
                                                                                           './/{*}Aktywa_B_III_1_A_4')

           assets_financial_short_term_other = convert_to_float(root, './/{*}Aktywa_B_III_1_B')
           assets_financial_short_term_other_before = convert_to_float_value_before(root, './/{*}Aktywa_B_III_1_B')
           assets_financial_short_term_other_shares_or_stocks = convert_to_float(root, './/{*}Aktywa_B_III_1_B_1')
           assets_financial_short_term_other_shares_or_stocks_before = convert_to_float_value_before(root,
                                                                                                './/{*}Aktywa_B_III_1_B_1')
           assets_financial_short_term_other_other_securities = convert_to_float(root, './/{*}Aktywa_B_III_1_B_2')
           assets_financial_short_term_other_other_securities_before = convert_to_float_value_before(root,
                                                                                                './/{*}Aktywa_B_III_1_B_2')
           assets_financial_short_term_other_loans_granted = convert_to_float(root, './/{*}Aktywa_B_III_1_B_3')
           assets_financial_short_term_other_loans_granted_before = convert_to_float_value_before(root,
                                                                                             './/{*}Aktywa_B_III_1_B_3')
           assets_financial_short_term_other_other = convert_to_float(root, './/{*}Aktywa_B_III_1_A_4')
           assets_financial_short_term_other_other_before = convert_to_float_value_before(root,
                                                                                            './/{*}Aktywa_B_III_1_B_4')
           assets_cash = convert_to_float(root, './/{*}Aktywa_B_III_1_C')
           assets_cash_before = convert_to_float_value_before(root, './/{*}Aktywa_B_III_1_C')

           assets_cash_cash_on_hand = convert_to_float(root, './/{*}Aktywa_B_III_1_C_1')
           assets_cash_cash_on_hand_before = convert_to_float_value_before(root, './/{*}Aktywa_B_III_1_C_1')
           assets_cash_cash_other = convert_to_float(root, './/{*}Aktywa_B_III_1_C_2')
           assets_cash_cash_other_before = convert_to_float_value_before(root, './/{*}Aktywa_B_III_1_C_2')
           assets_cash_other = convert_to_float(root, './/{*}Aktywa_B_III_1_C_3')
           assets_cash_other_before = convert_to_float_value_before(root, './/{*}Aktywa_B_III_1_C_3')

           investments_short_term_other = convert_to_float(root, './/{*}Aktywa_B_III_2')
           investments_short_term_other_before = convert_to_float_value_before(root, './/{*}Aktywa_B_III_2')

           prepayments_short_term = convert_to_float(root, './/{*}Aktywa_A_IV')
           prepayments_short_term_before = convert_to_float_value_before(root, './/{*}Aktywa_A_IV')

           equity = convert_to_float(root, './/{*}Pasywa_A')
           equity_before = convert_to_float_value_before(root, './/{*}Pasywa_A')

           capital_share = convert_to_float(root, './/{*}Pasywa_A_I')
           capital_share_before = convert_to_float_value_before(root, './/{*}Pasywa_A_I')

           capital_reserve = convert_to_float(root, './/{*}Pasywa_A_II')
           capital_reserve_before = convert_to_float_value_before(root, './/{*}Pasywa_A_II')
           capital_reserve_sales_value = convert_to_float(root, './/{*}Pasywa_A_II_1')
           capital_reserve_sales_value_before = convert_to_float_value_before(root, './/{*}Pasywa_A_II_1')

           capital_from_revaluation = convert_to_float(root, './/{*}Pasywa_A_III')
           capital_from_revaluation_before = convert_to_float_value_before(root, './/{*}Pasywa_A_III')

           capital_from_revaluation_fair_value = convert_to_float(root, './/{*}Pasywa_A_III_1')
           capital_from_revaluation_fair_value_before = convert_to_float_value_before(root, './/{*}Pasywa_A_III_1')

           capital_reserve_other = convert_to_float(root, './/{*}Pasywa_A_IV')
           capital_reserve_other_before = convert_to_float_value_before(root, './/{*}Pasywa_A_IV')
           capital_reserve_other_created_with_statutes = convert_to_float(root, './/{*}Pasywa_A_IV_1')
           capital_reserve_other_created_with_statutes_before = convert_to_float_value_before(root, './/{*}Pasywa_A_IV_1')
           capital_reserve_other_for_shares = convert_to_float(root, './/{*}Pasywa_A_IV_2')
           capital_reserve_other_for_shares_before = convert_to_float_value_before(root,
                                                                                              './/{*}Pasywa_A_IV_2')
           accumulated_from_previous_years = convert_to_float(root, './/{*}Pasywa_A_V')
           accumulated_from_previous_years_before = convert_to_float_value_before(root, './/{*}Pasywa_A_V')
           net_profit_or_loss = convert_to_float(root, './/{*}Pasywa_A_VI')
           net_profit_or_loss_before = convert_to_float_value_before(root, './/{*}Pasywa_A_VI')
           advanced_distributions = convert_to_float(root, './/{*}Pasywa_A_VII')
           advanced_distributions_before = convert_to_float_value_before(root, './/{*}Pasywa_A_VII')

           liabilities_and_provisions = convert_to_float(root, './/{*}Pasywa_B')
           liabilities_and_provisions_before = convert_to_float_value_before(root, './/{*}Pasywa_B')

           provisions = convert_to_float(root, './/{*}Pasywa_B_I')
           provisions_before = convert_to_float_value_before(root, './/{*}Pasywa_B_I')

           provision_for_income_tax = convert_to_float(root, './/{*}Pasywa_B_I_1')
           provision_for_income_tax_before = convert_to_float_value_before(root, './/{*}Pasywa_B_I_1')
           provision_for_employee_benefits = convert_to_float(root, './/{*}Pasywa_B_I_2')
           provision_for_employee_benefits_before = convert_to_float_value_before(root, './/{*}Pasywa_B_I_2')
           provision_long_term_for_employee_benefits = convert_to_float(root, './/{*}Pasywa_B_I_2_1')
           provision_long_term_for_employee_benefits_before = convert_to_float_value_before(root, './/{*}Pasywa_B_I_2_1')
           provision_short_term_for_employee_benefits = convert_to_float(root, './/{*}Pasywa_B_I_2_2')
           provision_short_term_for_employee_benefits_before = convert_to_float_value_before(root,
                                                                                            './/{*}Pasywa_B_I_2_2')
           provision_other = convert_to_float(root, './/{*}Pasywa_B_I_3')
           provision_other_before = convert_to_float_value_before(root, './/{*}Pasywa_B_I_3')
           provision_other_long_term = convert_to_float(root, './/{*}Pasywa_B_I_3_1')
           provision_other_long_term_before = convert_to_float_value_before(root, './/{*}Pasywa_B_I_3_1')
           provision_other_short_term = convert_to_float(root, './/{*}Pasywa_B_I_3_2')
           provision_other_short_term_before = convert_to_float_value_before(root, './/{*}Pasywa_B_I_3_2')

           liabilities_long_term = convert_to_float(root, './/{*}Pasywa_B_II')
           liabilities_long_term_before = convert_to_float_value_before(root, './/{*}Pasywa_B_II')

           liabilities_long_term_related = convert_to_float(root, './/{*}Pasywa_B_II_1')
           liabilities_long_term_related_before = convert_to_float_value_before(root, './/{*}Pasywa_B_II_1')
           liabilities_long_term_shares = convert_to_float(root, './/{*}Pasywa_B_II_2')
           liabilities_long_term_shares_before = convert_to_float_value_before(root, './/{*}Pasywa_B_II_2')
           liabilities_long_term_other = convert_to_float(root, './/{*}Pasywa_B_II_3')
           liabilities_long_term_other_before = convert_to_float_value_before(root, './/{*}Pasywa_B_II_3')
           liabilities_long_term_other_credits = convert_to_float(root, './/{*}Pasywa_B_II_3_A')
           liabilities_long_term_other_credits_before = convert_to_float_value_before(root, './/{*}Pasywa_B_II_3_A')
           liabilities_long_term_other_debt_securities = convert_to_float(root, './/{*}Pasywa_B_II_3_B')
           liabilities_long_term_other_debt_securities_before = convert_to_float_value_before(root, './/{*}Pasywa_B_II_3_B')
           liabilities_long_term_other_other_financial_liabilities = convert_to_float(root, './/{*}Pasywa_B_II_3_C')
           liabilities_long_term_other_other_financial_liabilities_before = convert_to_float_value_before(root,
                                                                                              './/{*}Pasywa_B_II_3_C')
           liabilities_long_term_other_promissory_obligations = convert_to_float(root, './/{*}Pasywa_B_II_3_D')
           liabilities_long_term_other_promissory_obligations_before = convert_to_float_value_before(root,
                                                                                                          './/{*}Pasywa_B_II_3_D')
           liabilities_long_term_other_other = convert_to_float(root, './/{*}Pasywa_B_II_3_E')
           liabilities_long_term_other_other_before = convert_to_float_value_before(root, './/{*}Pasywa_B_II_3_E')

           liabilities_short_therm = convert_to_float(root, './/{*}Pasywa_B_III')
           liabilities_short_therm_before = convert_to_float_value_before(root, './/{*}Pasywa_B_III')
           liabilities_short_term_related = convert_to_float(root, './/{*}Pasywa_B_III_1')
           liabilities_short_term_related_before = convert_to_float_value_before(root, './/{*}Pasywa_B_III_1')
           liabilities_short_term_related_trade_due_dates = convert_to_float(root, './/{*}Pasywa_B_III_1_A')
           liabilities_short_term_related_trade_due_dates_before = convert_to_float_value_before(root,
                                                                            './/{*}Pasywa_B_III_1_A')
           liabilities_short_term_related_trade_within_12 = convert_to_float(root, './/{*}Pasywa_B_III_1_A_1')
           liabilities_short_term_related_trade_within_12_before = convert_to_float_value_before(root,
                                                                           './/{*}Pasywa_B_III_1_A_1')
           liabilities_short_term_related_trade_more_12 = convert_to_float(root, './/{*}Pasywa_B_III_1_A_2')
           liabilities_short_term_related_trade_more_12_before = convert_to_float_value_before(root,
                                                                        './/{*}Pasywa_B_III_1_A_2')
           liabilities_short_term_related_other = convert_to_float(root, './/{*}Pasywa_B_III_1_B')
           liabilities_short_term_related_other_before = convert_to_float_value_before(root,
                                                                                      './/{*}Pasywa_B_III_1_B')

           liabilities_short_term_shares = convert_to_float(root, './/{*}Pasywa_B_III_2')
           liabilities_short_term_shares_before = convert_to_float_value_before(root, './/{*}Pasywa_B_III_2')
           liabilities_short_term_shares_trade_due_dates = convert_to_float(root, './/{*}Pasywa_B_III_2_A')
           liabilities_short_term_shares_trade_due_dates_before = convert_to_float_value_before(root,
                                                                                         './/{*}Pasywa_B_III_2_A')
           liabilities_short_term_shares_trade_within_12 = convert_to_float(root, './/{*}Pasywa_B_III_2_A_1')
           liabilities_short_term_shares_trade_within_12_before = convert_to_float_value_before(root,
                                                                                        './/{*}Pasywa_B_III_2_A_1')
           liabilities_short_term_shares_trade_more_12 = convert_to_float(root, './/{*}Pasywa_B_III_2_A_2')
           liabilities_short_term_shares_trade_more_12_before = convert_to_float_value_before(root,
                                                                                       './/{*}Pasywa_B_III_2_A_2')
           liabilities_short_term_shares_other = convert_to_float(root, './/{*}Pasywa_B_III_2_B')
           liabilities_short_term_shares_other_before = convert_to_float_value_before(root,
                                                                                       './/{*}Pasywa_B_III_2_B')

           liabilities_short_term_other = convert_to_float(root, './/{*}Pasywa_B_III_3')
           liabilities_short_term_other_before = convert_to_float_value_before(root, './/{*}Pasywa_B_III_3')
           liabilities_short_term_other_credits = convert_to_float(root, './/{*}Pasywa_B_III_3_A')
           liabilities_short_term_other_credits_before = convert_to_float_value_before(root,
                                                                                     './/{*}Pasywa_B_III_3_A')
           liabilities_short_term_other_debt_securities = convert_to_float(root, './/{*}Pasywa_B_III_3_B')
           liabilities_short_term_other_debt_securities_before = convert_to_float_value_before(root,
                                                                                  './/{*}Pasywa_B_III_3_B')
           liabilities_short_term_other_other_financial_liabilities = convert_to_float(root, './/{*}Pasywa_B_III_3_C')
           liabilities_short_term_other_other_financial_liabilities_before = convert_to_float_value_before(root,
                                                                                    './/{*}Pasywa_B_III_3_C')
           liabilities_short_term_other_trade_due_dates = convert_to_float(root, './/{*}Pasywa_B_III_3_D')
           liabilities_short_term_other_trade_due_dates_before = convert_to_float_value_before(root,
                                                                                      './/{*}Pasywa_B_III_3_D')
           liabilities_short_term_other_trade_within_12 = convert_to_float(root, './/{*}Pasywa_B_III_3_D_1')
           liabilities_short_term_other_trade_within_12_before = convert_to_float_value_before(root,
                                                                                               './/{*}Pasywa_B_III_3_D_1')
           liabilities_short_term_other_trade_more_12 = convert_to_float(root, './/{*}Pasywa_B_III_3_D_2')
           liabilities_short_term_other_trade_more_12_before = convert_to_float_value_before(root,
                                                                                               './/{*}Pasywa_B_III_3_D_2')
           liabilities_short_term_other_advances_for_deliveries = convert_to_float(root, './/{*}Pasywa_B_III_3_E')
           liabilities_short_term_other_advances_for_deliveries_before = convert_to_float_value_before(root,
                                                                                               './/{*}Pasywa_B_III_3_E')
           liabilities_short_term_other_promissory_obligations = convert_to_float(root, './/{*}Pasywa_B_III_3_F')
           liabilities_short_term_other_promissory_obligations_before = convert_to_float_value_before(root,
                                                                                                       './/{*}Pasywa_B_III_3_F')
           liabilities_short_term_other_tax = convert_to_float(root, './/{*}Pasywa_B_III_3_G')
           liabilities_short_term_other_tax_before = convert_to_float_value_before(root, './/{*}Pasywa_B_III_3_G')

           liabilities_short_term_other_payroll = convert_to_float(root, './/{*}Pasywa_B_III_3_H')
           liabilities_short_term_other_payroll_before = convert_to_float_value_before(root, './/{*}Pasywa_B_III_3_H')
           liabilities_short_term_other_other = convert_to_float(root, './/{*}Pasywa_B_III_3_I')
           liabilities_short_term_other_other_before = convert_to_float_value_before(root, './/{*}Pasywa_B_III_3_I')

           liabilities_short_term_special_funds = convert_to_float(root, './/{*}Pasywa_B_III_4')
           liabilities_short_term_special_funds_before = convert_to_float_value_before(root, './/{*}Pasywa_B_III_4')

           accruals = convert_to_float(root, './/{*}Pasywa_B_IV')
           accruals_before = convert_to_float_value_before(root, './/{*}Pasywa_B_IV')
           accruals_negative_goodwill = convert_to_float(root, './/{*}Pasywa_B_IV_1')
           accruals_negative_goodwill_before = convert_to_float_value_before(root, './/{*}Pasywa_B_IV_1')
           accruals_other = convert_to_float(root, './/{*}Pasywa_B_IV_2')
           accruals_other_before = convert_to_float_value_before(root, './/{*}Pasywa_B_IV_2')
           accruals_other_long_term = convert_to_float(root, './/{*}Pasywa_B_IV_2_1')
           accruals_other_long_term_before = convert_to_float_value_before(root, './/{*}Pasywa_B_IV_2_1')
           accruals_other_short_term = convert_to_float(root, './/{*}Pasywa_B_IV_2_2')
           accruals_other_short_term_before = convert_to_float_value_before(root, './/{*}Pasywa_B_IV_2_2')

           revenue = convert_to_float(root, './/{*}A')
           revenue_before = convert_to_float_value_before(root, './/{*}A')
           revenue_related = convert_to_float(root, './/{*}A_J')
           revenue_related_before = convert_to_float_value_before(root, './/{*}A_J')
           revenue_from_sale_products = convert_to_float(root, './/{*}A_I')
           revenue_from_sale_products_before = convert_to_float_value_before(root, './/{*}A_I')
           revenue_net_from_sale_goods = convert_to_float(root, './/{*}A_II')
           revenue_net_from_sale_goods_before = convert_to_float_value_before(root, './/{*}A_II')

           costs_of_products_goods = convert_to_float(root, './/{*}B')
           costs_of_products_goods_before = convert_to_float_value_before(root, './/{*}B')
           costs_of_products_goods_related = convert_to_float(root, './/{*}B_J')
           costs_of_products_goods_related_before = convert_to_float_value_before(root, './/{*}B_J')
           costs_of_producing_products = convert_to_float(root, './/{*}B_I')
           costs_of_producing_products_before = convert_to_float_value_before(root, './/{*}B_I')
           value_of_sold_goods = convert_to_float(root, './/{*}B_II')
           value_of_sold_goods_before = convert_to_float_value_before(root, './/{*}B_II')
           profit_gross_sales = convert_to_float(root, './/{*}C')
           profit_gross_sales_before = convert_to_float_value_before(root, './/{*}C')
           costs_selling = convert_to_float(root, './/{*}D')
           costs_selling_before = convert_to_float_value_before(root, './/{*}D')
           costs_general_administration = convert_to_float(root, './/{*}E')
           costs_general_administration_before = convert_to_float_value_before(root, './/{*}E')
           profit_on_sales = convert_to_float(root, './/{*}F')
           profit_on_sales_before = convert_to_float_value_before(root, './/{*}F')
           revenue_operating_other = convert_to_float(root, './/{*}G')
           revenue_operating_other_before = convert_to_float_value_before(root, './/{*}G')
           profit_on_sales_non_financial_assets = convert_to_float(root, './/{*}G_I')
           profit_on_sales_non_financial_assets_before = convert_to_float_value_before(root, './/{*}G_I')
           subsidies = convert_to_float(root, './/{*}G_II')
           subsidies_before = convert_to_float_value_before(root, './/{*}G_II')
           revaluation_non_financial_assets = convert_to_float(root, './/{*}G_III')
           revaluation_non_financial_assets_before = convert_to_float_value_before(root, './/{*}G_III')
           other_revenue_operating_other = convert_to_float(root, './/{*}G_IV')
           other_revenue_operating_other_before = convert_to_float_value_before(root, './/{*}G_IV')
           costs_operating_other = convert_to_float(root, './/{*}H')
           costs_operating_other_before = convert_to_float_value_before(root, './/{*}H')
           loss_on_sales_non_financial_assets = convert_to_float(root, './/{*}H_I')
           loss_on_sales_non_financial_assets_before = convert_to_float_value_before(root, './/{*}H_I')
           loss_revaluation_non_financial_assets = convert_to_float(root, './/{*}H_II')
           loss_revaluation_non_financial_assets_before = convert_to_float_value_before(root, './/{*}H_II')
           other_costs_operating_other = convert_to_float(root, './/{*}H_III')
           other_costs_operating_other_before = convert_to_float_value_before(root, './/{*}H_III')

           profit_from_operations = convert_to_float(root, './/{*}I')
           profit_from_operations_before = convert_to_float_value_before(root, './/{*}I')
           income_financial = convert_to_float(root, './/{*}J')
           income_financial_before = convert_to_float_value_before(root, './/{*}J')

           dividends_profit_shares = convert_to_float(root, './/{*}J_I')
           dividends_profit_shares_before = convert_to_float_value_before(root, './/{*}J_I')

           dividends_profit_shares_related = convert_to_float(root, './/{*}J_I_A')
           dividends_profit_shares_related_before = convert_to_float_value_before(root, './/{*}J_I_A')
           dividends_profit_shares_related_shares = convert_to_float(root, './/{*}J_I_A_I')
           dividends_profit_shares_related_shares_before = convert_to_float_value_before(root, './/{*}J_I_A_I')

           dividends_profit_shares_other = convert_to_float(root, './/{*}J_I_B')
           dividends_profit_shares_other_before = convert_to_float_value_before(root, './/{*}J_I_B')
           dividends_profit_shares_other_shares = convert_to_float(root, './/{*}J_I_B_I')
           dividends_profit_shares_other_shares_before = convert_to_float_value_before(root, './/{*}J_I_B_I')

           interest = convert_to_float(root, './/{*}J_II')
           interest_before = convert_to_float_value_before(root, './/{*}J_II')

           interest_related = convert_to_float(root, './/{*}J_II_A')
           interest_related_before = convert_to_float_value_before(root, './/{*}J_II_A')

           gain_disposal_financial_assets = convert_to_float(root, './/{*}J_III')
           gain_disposal_financial_assets_before = convert_to_float_value_before(root, './/{*}J_III')
           gain_disposal_financial_assets_related = convert_to_float(root, './/{*}J_III_A')
           gain_disposal_financial_assets_related_before = convert_to_float_value_before(root, './/{*}J_III_A')
           revaluation_financial_assets = convert_to_float(root, './/{*}J_IV')
           revaluation_financial_assets_before = convert_to_float_value_before(root, './/{*}J_IV')
           income_financial_other = convert_to_float(root, './/{*}J_V')
           income_financial_other_before = convert_to_float_value_before(root, './/{*}J_V')

           costs_financial = convert_to_float(root, './/{*}K')
           costs_financial_before = convert_to_float_value_before(root, './/{*}K')

           costs_financial_interest = convert_to_float(root, './/{*}K_I')
           costs_financial_interest_before = convert_to_float_value_before(root, './/{*}K_I')
           costs_financial_interest_related = convert_to_float(root, './/{*}K_I_J')
           costs_financial_interest_related_before = convert_to_float_value_before(root, './/{*}K_I_J')
           costs_financial_loss_disposal_financial_assets = convert_to_float(root, './/{*}K_II')
           costs_financial_loss_disposal_financial_assets_before = convert_to_float_value_before(root, './/{*}K_II')
           costs_financial_loss_disposal_financial_assets_related = convert_to_float(root, './/{*}K_II_J')
           costs_financial_loss_disposal_financial_assets_related_before = convert_to_float_value_before(root, './/{*}K_II_J')
           costs_financial_revaluation_financial_assets = convert_to_float(root, './/{*}K_III')
           costs_financial_revaluation_financial_assets_before = convert_to_float_value_before(root, './/{*}K_III')
           costs_financial_other = convert_to_float(root, './/{*}K_IV')
           costs_financial_other_before = convert_to_float_value_before(root, './/{*}K_IV')
           profit_loss_gross = convert_to_float(root, './/{*}L')
           profit_loss_gross_before = convert_to_float_value_before(root, './/{*}L')
           tax = convert_to_float(root, './/{*}M')
           tax_before = convert_to_float_value_before(root, './/{*}M')
           reductions_other = convert_to_float(root, './/{*}N')
           reductions_other_before = convert_to_float_value_before(root, './/{*}N')
           profit_loss_net = convert_to_float(root, './/{*}O')
           profit_loss_net_before = convert_to_float_value_before(root, './/{*}O')

           change_of_product_state = convert_to_float(root, './/{*}A_II')
           change_of_product_state_before = convert_to_float_value_before(root, './/{*}A_II')

           costs_of_producing_products_for_own_needs = convert_to_float(root, './/{*}A_III')
           costs_of_producing_products_for_own_needs_before = convert_to_float_value_before(root, './/{*}A_III')

           revenues_net_from_sale_goods = convert_to_float(root, './/{*}A_IV')
           revenues_net_from_sale_goods_before = convert_to_float_value_before(root, './/{*}A_IV')
           costs_operating_b = convert_to_float(root, './/{*}B')
           costs_operating_b_before = convert_to_float_value_before(root, './/{*}B')
           depreciation = convert_to_float(root, './/{*}B_I')
           depreciation_before = convert_to_float_value_before(root, './/{*}B_I')
           usage_materials_energy = convert_to_float(root, './/{*}B_II')
           usage_materials_energy_before = convert_to_float_value_before(root, './/{*}B_II')
           foreign_service = convert_to_float(root, './/{*}B_III')
           foreign_service_before = convert_to_float_value_before(root, './/{*}B_III')
           tax_and_fees = convert_to_float(root, './/{*}B_IV')
           tax_and_fees_before = convert_to_float_value_before(root, './/{*}B_IV')
           tax_excise = convert_to_float(root, './/{*}B_IV_1')
           tax_excise_before = convert_to_float_value_before(root, './/{*}B_IV_1')
           salaries = convert_to_float(root, './/{*}B_V')
           salaries_before = convert_to_float_value_before(root, './/{*}B_V')
           social_other_benefits = convert_to_float(root, './/{*}B_VI')
           social_other_benefits_before = convert_to_float_value_before(root, './/{*}B_VI')
           social_other_benefits_retirement = convert_to_float(root, './/{*}B_VI_1')
           social_other_benefits_retirement_before = convert_to_float_value_before(root, './/{*}B_VI_1')
           costs_operating_b_other_costs = convert_to_float(root, './/{*}B_VII')
           costs_operating_b_other_costs_before = convert_to_float_value_before(root, './/{*}B_VII')
           costs_operating_b_value_of_sold_goods = convert_to_float(root, './/{*}B_VIII')
           costs_operating_b_value_of_sold_goods_before = convert_to_float_value_before(root, './/{*}B_VIII')
           var_comparative_revenue_operating_other = convert_to_float(root, './/{*}D')
           var_comparative_revenue_operating_other_before = convert_to_float_value_before(root, './/{*}D')
           var_comparative_profit_on_sales_non_financial_assets = convert_to_float(root, './/{*}D_I')
           var_comparative_profit_on_sales_non_financial_assets_before = convert_to_float_value_before(root, './/{*}D_I')
           var_comparative_subsidies = convert_to_float(root, './/{*}D_II')
           var_comparative_subsidies_before = convert_to_float_value_before(root, './/{*}D_II')
           var_comparative_revaluation_non_financial_assets = convert_to_float(root, './/{*}D_III')
           var_comparative_revaluation_non_financial_assets_before = convert_to_float_value_before(root, './/{*}D_III')
           var_comparative_other_revenue_operating_other = convert_to_float(root, './/{*}D_IV')
           var_comparative_other_revenue_operating_other_before = convert_to_float_value_before(root, './/{*}D_IV')

           var_comparative_costs_operating_other = convert_to_float(root, './/{*}E')
           var_comparative_costs_operating_other_before = convert_to_float_value_before(root, './/{*}E')
           var_comparative_loss_on_sales_non_financial_assets = convert_to_float(root, './/{*}E_I')
           var_comparative_loss_on_sales_non_financial_assets_before = convert_to_float_value_before(root, './/{*}E_I')
           var_comparative_loss_revaluation_non_financial_assets = convert_to_float(root, './/{*}E_II')
           var_comparative_loss_revaluation_non_financial_assets_before = convert_to_float_value_before(root, './/{*}E_II')
           var_comparative_other_costs_operating_other = convert_to_float(root, './/{*}E_III')
           var_comparative_other_costs_operating_other_before = convert_to_float_value_before(root, './/{*}E_III')
           var_comparative_profit_from_operations = convert_to_float(root, './/{*}F')
           var_comparative_profit_from_operations_before = convert_to_float_value_before(root, './/{*}F')
           var_comparative_income_financial = convert_to_float(root, './/{*}G')
           var_comparative_income_financial_before = convert_to_float_value_before(root, './/{*}G')
           var_comparative_dividends_profit_shares = convert_to_float(root, './/{*}G_I')
           var_comparative_dividends_profit_shares_before = convert_to_float_value_before(root, './/{*}G_I')
           var_comparative_dividends_profit_shares_related = convert_to_float(root, './/{*}G_I_A')
           var_comparative_dividends_profit_shares_related_before = convert_to_float_value_before(root, './/{*}G_I_A')
           var_comparative_dividends_profit_shares_related_shares = convert_to_float(root, './/{*}G_I_A_1')
           var_comparative_dividends_profit_shares_related_shares_before = convert_to_float_value_before(root, './/{*}G_I_A_1')
           var_comparative_dividends_profit_shares_other = convert_to_float(root, './/{*}G_I_B')
           var_comparative_dividends_profit_shares_other_before = convert_to_float_value_before(root, './/{*}G_I_B')
           var_comparative_dividends_profit_shares_other_shares = convert_to_float(root, './/{*}G_I_B_I')
           var_comparative_dividends_profit_shares_other_shares_before = convert_to_float_value_before(root, './/{*}G_I_B_I')
           var_comparative_interest = convert_to_float(root, './/{*}G_II')
           var_comparative_interest_before = convert_to_float_value_before(root, './/{*}G_II')
           var_comparative_interest_related = convert_to_float(root, './/{*}G_II_A')
           var_comparative_interest_related_before = convert_to_float_value_before(root, './/{*}G_II_A')
           var_comparative_gain_disposal_financial_assets = convert_to_float(root, './/{*}G_III')
           var_comparative_gain_disposal_financial_assets_before = convert_to_float_value_before(root, './/{*}G_III')
           var_comparative_gain_disposal_financial_assets_related = convert_to_float(root, './/{*}G_III_A')
           var_comparative_gain_disposal_financial_assets_related_before = convert_to_float_value_before(root, './/{*}G_III_A')
           var_comparative_revaluation_financial_assets = convert_to_float(root, './/{*}G_IV')
           var_comparative_revaluation_financial_assets_before = convert_to_float_value_before(root, './/{*}G_IV')
           var_comparative_income_financial_other = convert_to_float(root, './/{*}G_V')
           var_comparative_income_financial_other_before = convert_to_float_value_before(root, './/{*}G_V')

           var_comparative_costs_financial = convert_to_float(root, './/{*}H')
           var_comparative_costs_financial_before = convert_to_float_value_before(root, './/{*}H')
           var_comparative_costs_financial_interest = convert_to_float(root, './/{*}H_I')
           var_comparative_costs_financial_interest_before = convert_to_float_value_before(root, './/{*}H_I')
           var_comparative_costs_financial_interest_related = convert_to_float(root, './/{*}H_I_J')
           var_comparative_costs_financial_interest_related_before = convert_to_float_value_before(root, './/{*}H_I_J')
           var_comparative_costs_financial_loss_disposal_financial_assets = convert_to_float(root, './/{*}H_II')
           var_comparative_costs_financial_loss_disposal_financial_assets_before = convert_to_float_value_before(root, './/{*}H_II')
           var_comparative_costs_financial_loss_disposal_financial_assets_related = convert_to_float(root, './/{*}H_II_J')
           var_comparative_costs_financial_loss_disposal_financial_assets_related_before = convert_to_float_value_before(root,
                                                                                                        './/{*}H_II_J')
           var_comparative_costs_financial_revaluation_financial_assets = convert_to_float(root, './/{*}H_III')
           var_comparative_costs_financial_revaluation_financial_assets_before = convert_to_float_value_before(root, './/{*}H_III')
           var_comparative_costs_financial_other = convert_to_float(root, './/{*}H_IV')
           var_comparative_costs_financial_other_before = convert_to_float_value_before(root, './/{*}H_IV')

           var_comparative_profit_loss_gross = convert_to_float(root, './/{*}I')
           var_comparative_profit_loss_gross_before = convert_to_float_value_before(root, './/{*}I')
           var_comparative_tax = convert_to_float(root, './/{*}J')
           var_comparative_tax_before = convert_to_float_value_before(root, './/{*}J')
           var_comparative_reductions_other = convert_to_float(root, './/{*}K')
           var_comparative_reductions_other_before = convert_to_float_value_before(root, './/{*}K')
           var_comparative_profit_loss_net = convert_to_float(root, './/{*}L')
           var_comparative_profit_loss_net_before = convert_to_float_value_before(root, './/{*}L')

           opening_balance_equity = convert_to_float(root, './/{*}ZestZmianWKapitale')
           opening_balance_equity_before = convert_to_float_value_before(root, './/{*}ZestZmianWKapitale')

           changes_accounting_policies = convert_to_float(root, './/{*}I_1')
           changes_accounting_policies_before = convert_to_float_value_before(root, './/{*}I_1')

           error_corrections = convert_to_float(root, './/{*}I_2')
           error_corrections_before = convert_to_float_value_before(root, './/{*}I_2')

           opening_balance_equity_after_adjustments = convert_to_float(root, './/{*}IA')
           opening_balance_equity_after_adjustments_before = convert_to_float_value_before(root, './/{*}IA')

           opening_balance_share_capital = convert_to_float(root, './/{*}IA_1')
           opening_balance_share_capital_before = convert_to_float_value_before(root, './/{*}IA_1')

           opening_balance_share_capital_changes = convert_to_float(root, './/{*}IA_1_1')
           opening_balance_share_capital_changes_before = convert_to_float_value_before(root, './/{*}IA_1_1')
           opening_balance_share_capital_incrase = convert_to_float(root, './/{*}IA_1_1_A')
           opening_balance_share_capital_incrase_before = convert_to_float_value_before(root, './/{*}IA_1_1_A')
           opening_balance_share_capital_incrase_of_shares = convert_to_float(root, './/{*}IA_1_1_A_1')
           opening_balance_share_capital_incrase_of_shares_before = convert_to_float_value_before(root,
                                                                                                  './/{*}IA_1_1_A_1')
           opening_balance_share_capital_decrease = convert_to_float(root, './/{*}IA_1_1_B')
           opening_balance_share_capital_decrease_before = convert_to_float_value_before(root, './/{*}IA_1_1_B')
           opening_balance_share_capital_decreasee_of_shares = convert_to_float(root, './/{*}IA_1_1_B_1')
           opening_balance_share_capital_decreasee_of_shares_before = convert_to_float_value_before(root,
                                                                                                    './/{*}IA_1_1_B_1')
           closing_balance_share_capital = convert_to_float(root, './/{*}IA_1_2')
           closing_balance_share_capital_before = convert_to_float_value_before(root, './/{*}IA_1_2')

           opening_balance_supplementary_capital = convert_to_float(root, './/{*}IA_2')
           opening_balance_supplementary_capital_before = convert_to_float_value_before(root, './/{*}IA_2')
           opening_balance_supplementary_capital_changes = convert_to_float(root, './/{*}IA_2_1')
           opening_balance_supplementary_capital_changes_before = convert_to_float_value_before(root, './/{*}IA_2_1')
           opening_balance_supplementary_capital_incrase = convert_to_float(root, './/{*}IA_2_1_A')
           opening_balance_supplementary_capital_incrase_before = convert_to_float_value_before(root, './/{*}IA_2_1_A')
           opening_balance_supplementary_capital_issue_of_shares = convert_to_float(root, './/{*}IA_2_1_A_1')
           opening_balance_supplementary_capital_issue_of_shares_before = convert_to_float_value_before(root,
                                                                                                        './/{*}IA_2_1_A_1')
           opening_balance_supplementary_capital_profit_distribution = convert_to_float(root, './/{*}IA_2_1_A_2')
           opening_balance_supplementary_capital_profit_distribution_before = convert_to_float_value_before(root,
                                                                                                            './/{*}IA_2_1_A_2')
           opening_balance_supplementary_capital_profit_distribution_statutory = convert_to_float(root,
                                                                                                  './/{*}IA_2_1_A_3')
           opening_balance_supplementary_capital_profit_distribution_statutory_before = convert_to_float_value_before(
               root,
               './/{*}IA_2_1_A_3')

           opening_balance_supplementary_capital_decreasee = convert_to_float(root, './/{*}IA_2_1_B')
           opening_balance_supplementary_capital_decreasee_before = convert_to_float_value_before(root,
                                                                                                  './/{*}IA_2_1_B')

           opening_balance_supplementary_capital_decreasee_title = root.find('.//{*}IA_2_1_B')
           if opening_balance_supplementary_capital_decreasee_title is not None:
               opening_balance_supplementary_capital_decreasee_title = opening_balance_supplementary_capital_decreasee_title.find(
               './/{*}NazwaPozycji').text

           opening_balance_supplementary_capital_loss_coverage = convert_to_float(root, './/{*}IA_2_1_B_1')
           opening_balance_supplementary_capital_loss_coverage_before = convert_to_float_value_before(root,
                                                                                                      './/{*}IA_2_1_B_1')
           opening_balance_supplementary_capital_dividend_root = root.find('.//{*}IA_2_1_B')
           if opening_balance_supplementary_capital_dividend_root is not None:
               opening_balance_supplementary_capital_dividend = opening_balance_supplementary_capital_dividend_root.find(
               './/{*}KwotyPozycji')
               if opening_balance_supplementary_capital_dividend is not None:
                   opening_balance_supplementary_capital_dividend_value = opening_balance_supplementary_capital_dividend.find(
               './/{*}KwotaA').text
               opening_balance_supplementary_capital_dividend_value = round(float(opening_balance_supplementary_capital_dividend_value), 2)
               opening_balance_supplementary_capital_dividend_value_before = opening_balance_supplementary_capital_dividend.find(
               './/{*}KwotaB').text
               opening_balance_supplementary_capital_dividend_value = round(float(opening_balance_supplementary_capital_dividend_value), 2)

           closing_balance_supplementary_capital = convert_to_float(root, './/{*}IA_2_2')
           closing_balance_supplementary_capital_before = convert_to_float_value_before(root, './/{*}IA_2_2')

           opening_balance_reveluation = convert_to_float(root, './/{*}IA_3')
           opening_balance_reveluation_before = convert_to_float_value_before(root, './/{*}IA_3')
           opening_balance_reveluation_changes = convert_to_float(root, './/{*}IA_3_1')
           opening_balance_reveluation_changes_before = convert_to_float_value_before(root, './/{*}IA_3_1')
           opening_balance_reveluation_changes_decreasee = convert_to_float(root, './/{*}IA_3_1_B')
           opening_balance_reveluation_changes_decreasee_before = convert_to_float_value_before(root, './/{*}IA_3_1_B')
           opening_balance_reveluation_changes_sales_assets = convert_to_float(root, './/{*}IA_3_1_B_1')
           opening_balance_reveluation_changes_sales_assets_before = convert_to_float_value_before(root,
                                                                                                   './/{*}IA_3_1_B_1')
           closing_balance_reveluation = convert_to_float(root, './/{*}IA_3_2')
           closing_balance_reveluation_before = convert_to_float_value_before(root, './/{*}IA_3_2')
           opening_balance_other_capitals = convert_to_float(root, './/{*}IA_4')
           opening_balance_other_capitals_before = convert_to_float_value_before(root, './/{*}IA_4')
           opening_balance_other_capitals_bz = convert_to_float(root, './/{*}IA_4_2')
           opening_balance_other_capitals_bz_before = convert_to_float_value_before(root, './/{*}IA_4_2')
           opening_balance_profit_previous_years = convert_to_float(root, './/{*}IA_5')
           opening_balance_profit_previous_years_before = convert_to_float_value_before(root, './/{*}IA_5')
           opening_balance_profit_previous_years_profit = convert_to_float(root, './/{*}IA_5_1')
           opening_balance_profit_previous_years_profit_before = convert_to_float_value_before(root, './/{*}IA_5_1')
           opening_balance_profit_previous_years_changes_policies = convert_to_float(root, './/{*}IA_5_1_1')
           opening_balance_profit_previous_years_changes_policies_before = convert_to_float_value_before(root,
                                                                                                         './/{*}IA_5_1_1')
           opening_balance_profit_previous_years_error_corrections = convert_to_float(root, './/{*}IA_5_1_2')
           opening_balance_profit_previous_years_error_corrections_before = convert_to_float_value_before(root,
                                                                                                          './/{*}IA_5_1_2')

           opening_balance_profit_previous_years_after_adj = convert_to_float(root, './/{*}IA_5_2')
           opening_balance_profit_previous_years_after_adj_before = convert_to_float_value_before(root, './/{*}IA_5_2')
           opening_balance_profit_previous_years_after_adj_increase = convert_to_float(root, './/{*}IA_5_2_A')
           opening_balance_profit_previous_years_after_adj_increase_before = convert_to_float_value_before(root,
                                                                                                           './/{*}IA_5_2_A')
           opening_balance_profit_previous_years_after_adj_distribution = convert_to_float(root, './/{*}IA_5_2_A_1')
           opening_balance_profit_previous_years_after_adj_distribution_before = convert_to_float_value_before(root,
                                                                                                               './/{*}IA_5_2_A_1')
           opening_balance_profit_previous_years_after_adj_decrease_all = convert_to_float(root, './/{*}IA_5_2_B')
           opening_balance_profit_previous_years_after_adj_decrease_all_before = convert_to_float_value_before(root,
                                                                                                               './/{*}IA_5_2_B')

           opening_balance_profit_previous_years_after_adj_decrease_root = root.find('.//{*}IA_5_2_B')
           if opening_balance_profit_previous_years_after_adj_decrease_root is not None:
               opening_balance_profit_previous_years_after_adj_decrease_title = opening_balance_profit_previous_years_after_adj_decrease_root.find(
               './/{*}NazwaPozycji')
               opening_balance_profit_previous_years_after_adj_decrease_title = opening_balance_profit_previous_years_after_adj_decrease_title.text
               opening_balance_profit_previous_years_after_adj_decrease = opening_balance_profit_previous_years_after_adj_decrease_root.find(
               './/{*}KwotyPozycji')
               opening_balance_profit_previous_years_after_adj_decrease_value = opening_balance_profit_previous_years_after_adj_decrease.find(
               './/{*}KwotaA').text
               opening_balance_profit_previous_years_after_adj_decrease_value = round(float(opening_balance_profit_previous_years_after_adj_decrease_value), 2)
               opening_balance_profit_previous_years_after_adj_decrease_value_before = opening_balance_profit_previous_years_after_adj_decrease.find(
               './/{*}KwotaB').text
               opening_balance_profit_previous_years_after_adj_decrease_value_before = round(float(opening_balance_profit_previous_years_after_adj_decrease_value_before), 2)

           closing_balance_profit_previous_years = convert_to_float(root, './/{*}IA_5_3')
           closing_balance_profit_previous_years_before = convert_to_float_value_before(root, './/{*}IA_5_3')

           opening_balance_loss_profit_previous_years = convert_to_float(root, './/{*}IA_5_4')
           opening_balance_loss_profit_previous_years_before = convert_to_float_value_before(root, './/{*}IA_5_4')
           opening_balance_loss_profit_previous_years_changes_policies = convert_to_float(root, './/{*}IA_5_4_1')
           opening_balance_loss_profit_previous_years_changes_policies_before = convert_to_float_value_before(root,
                                                                                                              './/{*}IA_5_4_1')
           opening_balance_loss_profit_previous_years_error_corrections = convert_to_float(root, './/{*}IA_5_4_2')
           opening_balance_loss_profit_previous_years_error_corrections_before = convert_to_float_value_before(root,
                                                                                                               './/{*}IA_5_4_2')
           opening_balance_loss_profit_previous_years_after_adj = convert_to_float(root, './/{*}IA_5_5')
           opening_balance_loss_profit_previous_years_after_adj_before = convert_to_float_value_before(root,
                                                                                                       './/{*}IA_5_5')

           opening_balance_loss_profit_previous_years_after_adj_increase = convert_to_float(root, './/{*}IA_5_5_A')
           opening_balance_loss_profit_previous_years_after_adj_increase_before = convert_to_float_value_before(root,
                                                                                                                './/{*}IA_5_5_A')
           opening_balance_loss_profit_previous_years_loss_to_cover = convert_to_float(root, './/{*}IA_5_5_A_1')
           opening_balance_loss_profit_previous_years_loss_to_cover_before = convert_to_float_value_before(root,
                                                                                                           './/{*}IA_5_5_A_1')
           closing_balance_loss_profit_previous_years = convert_to_float(root, './/{*}IA_5_6')
           closing_balance_loss_profit_previous_years_before = convert_to_float_value_before(root, './/{*}IA_5_6')
           closing_balance_loss_or_profit_previous_years = convert_to_float(root, './/{*}IA_5_7')
           closing_balance_loss_or_profit_previous_years_before = convert_to_float_value_before(root, './/{*}IA_5_7')
           result_net = convert_to_float(root, './/{*}IA_6')
           result_net_before = convert_to_float_value_before(root, './/{*}IA_6')
           result_net_profit = convert_to_float(root, './/{*}IA_6_A')
           result_net_profit_before = convert_to_float_value_before(root, './/{*}IA_6_A')
           result_net_loss = convert_to_float(root, './/{*}IA_6_B')
           result_net_loss_before = convert_to_float_value_before(root, './/{*}IA_6_B')
           result_net_write_offs = convert_to_float(root, './/{*}IA_6_C')
           result_net_write_offs_before = convert_to_float_value_before(root, './/{*}IA_6_C')

           closing_balance_equity = convert_to_float(root, './/{*}II')
           closing_balance_equity_before = convert_to_float_value_before(root, './/{*}II')
           closing_balance_equity_after_adj = convert_to_float(root, './/{*}III')
           closing_balance_equity_after_adj_before = convert_to_float_value_before(root, './/{*}III')

           cash_flow_operating = convert_to_float(root, './/{*}A_I')
           cash_flow_operating_before = convert_to_float_value_before(root, './/{*}A_I')
           if code_cash_flow is not None:
               cash_flow_operating = convert_to_float(code_cash_flow, './/{*}A_I')
               cash_flow_operating_before = convert_to_float_value_before(code_cash_flow, './/{*}A_I')
               cash_flow_operating_adjustments = convert_to_float(code_cash_flow, './/{*}A_II')
               cash_flow_operating_adjustments_before = convert_to_float_value_before(code_cash_flow, './/{*}A_II')
               cash_flow_operating_amortisation = convert_to_float(code_cash_flow, './/{*}A_II_1')
               cash_flow_operating_amortisation_before = convert_to_float_value_before(code_cash_flow, './/{*}A_II_1')
               cash_flow_operating_exchange_gains = convert_to_float(code_cash_flow, './/{*}A_II_2')
               cash_flow_operating_exchange_gains_before = convert_to_float_value_before(code_cash_flow, './/{*}A_II_2')
               cash_flow_operating_dividend = convert_to_float(code_cash_flow, './/{*}A_II_3')
               cash_flow_operating_dividend_before = convert_to_float_value_before(code_cash_flow, './/{*}A_II_3')
               cash_flow_operating_profit_or_loss_investment = convert_to_float(code_cash_flow, './/{*}A_II_4')
               cash_flow_operating_profit_or_loss_investment_before = convert_to_float_value_before(code_cash_flow, './/{*}A_II_4')
               cash_flow_operating_provisions_change = convert_to_float(code_cash_flow, './/{*}A_II_5')
               cash_flow_operating_provisions_change_before = convert_to_float_value_before(code_cash_flow,
                                                                                                './/{*}A_II_5')
               cash_flow_operating_inventory_change = convert_to_float(code_cash_flow, './/{*}A_II_6')
               cash_flow_operating_inventory_change_before = convert_to_float_value_before(code_cash_flow,
                                                                                                './/{*}A_II_6')
               cash_flow_operating_receivables_change = convert_to_float(code_cash_flow, './/{*}A_II_7')
               cash_flow_operating_receivables_change_before = convert_to_float_value_before(code_cash_flow,
                                                                                       './/{*}A_II_7')
               cash_flow_operating_short_term_liabilities_change = convert_to_float(code_cash_flow, './/{*}A_II_8')
               cash_flow_operating_short_term_liabilities_change_before = convert_to_float_value_before(code_cash_flow,
                                                                                       './/{*}A_II_8')
               cash_flow_operating_prepayments_change = convert_to_float(code_cash_flow, './/{*}A_II_9')
               cash_flow_operating_prepayments_change_before = convert_to_float_value_before(code_cash_flow,
                                                                                       './/{*}A_II_9')
               cash_flow_operating_other_adjustments = convert_to_float(code_cash_flow, './/{*}A_II_10')
               cash_flow_operating_other_adjustments_before = convert_to_float_value_before(code_cash_flow,
                                                                                       './/{*}A_II_10')
               net_cash_flow_operating = convert_to_float(code_cash_flow, './/{*}A_III')
               net_cash_flow_operating_before = convert_to_float_value_before(code_cash_flow, './/{*}A_III')
               cash_flow_investment_inflows = convert_to_float(code_cash_flow, './/{*}B_I')
               cash_flow_investment_inflows_before = convert_to_float_value_before(code_cash_flow, './/{*}B_I')
               cash_flow_investment_disposal_of_intangible = convert_to_float(code_cash_flow, './/{*}B_I_1')
               cash_flow_investment_disposal_of_intangible_before = convert_to_float_value_before(code_cash_flow, './/{*}B_I_1')
               cash_flow_investment_disposal_of_investments = convert_to_float(code_cash_flow, './/{*}B_I_2')
               cash_flow_investment_disposal_of_investments_before = convert_to_float_value_before(code_cash_flow,
                                                                                              './/{*}B_I_2')
               cash_flow_investment_financial_assets = convert_to_float(code_cash_flow, './/{*}B_I_3')
               cash_flow_investment_financial_assets_before = convert_to_float_value_before(code_cash_flow,
                                                                                    './/{*}B_I_3')
               cash_flow_investment_financial_assets_related = convert_to_float(code_cash_flow, './/{*}B_I_3_A')
               cash_flow_investment_financial_assets_related_before = convert_to_float_value_before(code_cash_flow,
                                                                             './/{*}B_I_3_A')
               cash_flow_investment_financial_assets_other_related = convert_to_float(code_cash_flow, './/{*}B_I_3_B')
               cash_flow_investment_financial_assets_other_related_before = convert_to_float_value_before(code_cash_flow,
                                                                                     './/{*}B_I_3_B')
               cash_flow_investment_sales_assets = convert_to_float(code_cash_flow, './/{*}B_I_3_B_1')
               cash_flow_investment_sales_assets_before = convert_to_float_value_before(code_cash_flow, './/{*}B_I_3_B_1')
               cash_flow_investment_dividend = convert_to_float(code_cash_flow, './/{*}B_I_3_B_2')
               cash_flow_investment_dividend_before = convert_to_float_value_before(code_cash_flow, './/{*}B_I_3_B_2')
               cash_flow_investment_repayment_granted = convert_to_float(code_cash_flow, './/{*}B_I_3_B_3')
               cash_flow_investment_repayment_granted_before = convert_to_float_value_before(code_cash_flow, './/{*}B_I_3_B_3')
               cash_flow_investment_interest = convert_to_float(code_cash_flow, './/{*}B_I_3_B_4')
               cash_flow_investment_interest_before = convert_to_float_value_before(code_cash_flow, './/{*}B_I_3_B_4')
               cash_flow_investment_other_inflows_assets = convert_to_float(code_cash_flow, './/{*}B_I_3_B_5')
               cash_flow_investment_other_inflows_assets_before = convert_to_float_value_before(code_cash_flow, './/{*}B_I_3_B_5')
               cash_flow_investment_other_inflows_investment = convert_to_float(code_cash_flow, './/{*}B_I_4')
               cash_flow_investment_other_inflows_investment_before = convert_to_float_value_before(code_cash_flow,
                                                                             './/{*}B_I_4')
               cash_flow_investment_outflows = convert_to_float(code_cash_flow, './/{*}B_II')
               cash_flow_investment_outflows_before = convert_to_float_value_before(code_cash_flow, './/{*}B_II')
               cash_flow_investment_purchase_of_intangible = convert_to_float(code_cash_flow, './/{*}B_II_1')
               cash_flow_investment_purchase_of_intangible_before = convert_to_float_value_before(code_cash_flow,
                                                                                   './/{*}B_II_1')
               cash_flow_investment_purchase_of_investments = convert_to_float(code_cash_flow, './/{*}B_II_2')
               cash_flow_investment_purchase_of_investments_before = convert_to_float_value_before(code_cash_flow,
                                                                                    './/{*}B_II_2')
               cash_flow_investment_purchase_financial_assets = convert_to_float(code_cash_flow, './/{*}B_II_3')
               cash_flow_investment_purchase_financial_assets_before = convert_to_float_value_before(code_cash_flow,
                                                                             './/{*}B_II_3')
               cash_flow_investment_purchase_financial_assets_related = convert_to_float(code_cash_flow, './/{*}B_II_3_A')
               cash_flow_investment_purchase_financial_assets_related_before = convert_to_float_value_before(code_cash_flow,
                                                                                                './/{*}B_II_3_A')
               cash_flow_investment_purchase_financial_assets_other_related = convert_to_float(code_cash_flow, './/{*}B_II_3_B')
               cash_flow_investment_purchase_financial_assets_other_related_before = convert_to_float_value_before(code_cash_flow,
                                                                                           './/{*}B_II_3_B')
               cash_flow_investment_purchase_assets = convert_to_float(code_cash_flow, './/{*}B_II_3_B_1')
               cash_flow_investment_purchase_assets_before = convert_to_float_value_before(code_cash_flow, './/{*}B_II_3_B_1')
               cash_flow_investment_loans_long_term = convert_to_float(code_cash_flow, './/{*}B_II_3_B_2')
               cash_flow_investment_loans_long_term_before = convert_to_float_value_before(code_cash_flow, './/{*}B_II_3_B_2')
               cash_flow_investment_other_outflows_investment = convert_to_float(code_cash_flow, './/{*}B_II_4')
               cash_flow_investment_other_outflows_investment_before = convert_to_float_value_before(code_cash_flow,
                                                                                     './/{*}B_II_4')
               net_cash_flow_investment = convert_to_float(code_cash_flow, './/{*}B_III')
               net_cash_flow_investment_before = convert_to_float_value_before(code_cash_flow, './/{*}B_III')
               cash_flow_financial_inflows = convert_to_float(code_cash_flow, './/{*}C_I')
               cash_flow_financial_inflows_before = convert_to_float_value_before(code_cash_flow, './/{*}C_I')
               cash_flow_financial_net_inflows = convert_to_float(code_cash_flow, './/{*}C_I_1')
               cash_flow_financial_net_inflows_before = convert_to_float_value_before(code_cash_flow, './/{*}C_I_1')
               cash_flow_financial_credits = convert_to_float(code_cash_flow, './/{*}C_I_2')
               cash_flow_financial_credits_before = convert_to_float_value_before(code_cash_flow, './/{*}C_I_2')
               cash_flow_financial_issuance = convert_to_float(code_cash_flow, './/{*}C_I_3')
               cash_flow_financial_issuance_before = convert_to_float_value_before(code_cash_flow, './/{*}C_I_3')
               cash_flow_financial_other_inflows = convert_to_float(code_cash_flow, './/{*}C_I_4')
               cash_flow_financial_other_inflows_before = convert_to_float_value_before(code_cash_flow, './/{*}C_I_4')
               cash_flow_financial_outflows = convert_to_float(code_cash_flow, './/{*}C_II')
               cash_flow_financial_outflows_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II')
               cash_flow_financial_purchase_shares = convert_to_float(code_cash_flow, './/{*}C_II_1')
               cash_flow_financial_purchase_shares_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II_1')
               cash_flow_financial_dividend = convert_to_float(code_cash_flow, './/{*}C_II_2')
               cash_flow_financial_dividend_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II_2')
               cash_flow_financial_profit_distribution = convert_to_float(code_cash_flow, './/{*}C_II_3')
               cash_flow_financial_profit_distribution_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II_3')
               cash_flow_financial_repayment = convert_to_float(code_cash_flow, './/{*}C_II_4')
               cash_flow_financial_repayment_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II_4')
               cash_flow_financial_redemption = convert_to_float(code_cash_flow, './/{*}C_II_5')
               cash_flow_financial_redemption_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II_5')
               cash_flow_financial_other_payment = convert_to_float(code_cash_flow, './/{*}C_II_6')
               cash_flow_financial_other_payment_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II_6')
               cash_flow_financial_leases = convert_to_float(code_cash_flow, './/{*}C_II_7')
               cash_flow_financial_leases_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II_7')
               cash_flow_financial_interest = convert_to_float(code_cash_flow, './/{*}C_II_8')
               cash_flow_financial_interest_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II_8')
               cash_flow_financial_other_outflows = convert_to_float(code_cash_flow, './/{*}C_II_9')
               cash_flow_financial_other_outflows_before = convert_to_float_value_before(code_cash_flow, './/{*}C_II_9')
               net_cash_flow_financial = convert_to_float(code_cash_flow, './/{*}C_III')
               net_cash_flow_financial_before = convert_to_float_value_before(code_cash_flow, './/{*}C_III')
               total_net_cash_flow = convert_to_float(code_cash_flow, './/{*}D')
               total_net_cash_flow_before = convert_to_float_value_before(code_cash_flow, './/{*}D')
               cash_flow_balance_sheet = convert_to_float(code_cash_flow, './/{*}E')
               cash_flow_balance_sheet_before = convert_to_float_value_before(code_cash_flow, './/{*}E')
               cash_flow_balance_sheet_exchange_change = convert_to_float(code_cash_flow, './/{*}E_1')
               cash_flow_balance_sheet_exchange_change_before = convert_to_float_value_before(code_cash_flow, './/{*}E_1')
               opening_cash_balance = convert_to_float(code_cash_flow, './/{*}F')
               opening_cash_balance_before = convert_to_float_value_before(code_cash_flow, './/{*}F')
               closing_cash_balance = convert_to_float(code_cash_flow, './/{*}G')
               closing_cash_balance_before = convert_to_float_value_before(code_cash_flow, './/{*}G')
               closing_cash_balance_of_limited = convert_to_float(code_cash_flow, './/{*}G_1')
               closing_cash_balance_of_limited_before = convert_to_float_value_before(code_cash_flow, './/{*}G_1')

       return render(request, 'file_detail.html', locals())





