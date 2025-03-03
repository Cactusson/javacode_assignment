from django.urls import path

from wallets import views


urlpatterns = [
    path("wallets/", views.WalletList.as_view(), name="wallet-list"),
    path("wallets/<uuid:uuid>/", views.WalletDetail.as_view(), name="wallet-detail"),
    path(
        "wallets/<uuid:uuid>/operation/",
        views.WalletOperation.as_view(),
        name="wallet-operation",
    ),
]
