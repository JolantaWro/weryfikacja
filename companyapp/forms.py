from django import forms


class AddFileForm(forms.Form):
   file_name = forms.FileField()


class RatiosAddForm(forms.Form):
    nazwa_firmy = forms.CharField(max_length=255)
    numer_NIP = forms.IntegerField()
    rok = forms.IntegerField()
    aktywa_trwałe = forms.FloatField()
    aktywa_obrotowe = forms.FloatField()
    zapasy = forms.FloatField()
    należności_krótkoterminowe = forms.FloatField()
    należności_handlowe = forms.FloatField()
    należności_podatkowe = forms.FloatField()
    inwestycje_krótkoterminowe = forms.FloatField()
    środki_pieniężne = forms.FloatField()
    kapitał_podstawowy = forms.FloatField()
    rezerwy_i_rozliczenia_międzyokresowe = forms.FloatField()
    zobowiązania_długoterminowe = forms.FloatField()
    zobowiązania_długoterminowe_finansowe = forms.FloatField()
    zobowiązania_krótkoterminowe = forms.FloatField()
    zobowiązania_krótkoterminowe_finansowe = forms.FloatField()
    zobowiązania_handlowe = forms.FloatField()
    przychody = forms.FloatField()
    wynik_z_działalności_operacyjnej = forms.FloatField()
    amortyzacja = forms.FloatField()
    wynik_brutto = forms.FloatField()
    podatek_dochodowy = forms.FloatField()


















