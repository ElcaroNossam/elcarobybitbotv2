from django.urls import path

from .views import screener_list_api, symbol_detail_api, symbols_list_api, screener_latest_api, liquidations_api

app_name = "api"

urlpatterns = [
    path("screener/", screener_list_api, name="screener_list"),
    path("screener/latest/", screener_latest_api, name="screener_latest"),
    path("liquidations/", liquidations_api, name="liquidations"),
    path("symbol/<str:symbol>/", symbol_detail_api, name="symbol_detail"),
    path("symbols/", symbols_list_api, name="symbols_list"),
]


