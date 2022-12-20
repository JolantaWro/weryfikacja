"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from companyapp.views import IndexView, RatiosAddFile, RatiosAdd, RatiosEdit, RatiosViewFile, FileDetail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name="index"),
    path('file_add/', RatiosAddFile.as_view(), name="file_add"),
    path('file_detail/', FileDetail.as_view(), name="file_detail"),
    path('ratios_link/', RatiosViewFile.as_view(), name="ratios_link"),
    path('ratios_add/', RatiosAdd.as_view(), name="ratios_add"),
    # path('ratios_edit/<str:liabilities_long_therm_financial>/<str:liabilities_short_therm_financial>/', RatiosEdit.as_view(), name="ratios_edit"),
    path('ratios_edit/<str:company_name>/<str:number_nip>/<int:year_result>/<str:assets_fixed>/<str:assets_current>/<str:stock>/<str:receivables_short_term>/<str:receivables_trade>/<str:receivables_tax>/<str:investments_short_term>/<str:assets_cash>/<str:capital_share>/<str:provision_and_accruals>/<str:liabilities_long_therm>/<str:liabilities_long_therm_financial>/<str:liabilities_short_therm>/<str:liabilities_short_therm_financial>/<str:liabilities_trade>/<str:revenue>/<str:profit_operating>/<str:depreciation>/<str:profit_gross>/<str:tax_income>', RatiosEdit.as_view(), name="ratios_edit"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)