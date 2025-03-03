import decimal

from rest_framework import serializers

from wallets.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=decimal.Decimal("0"),
        default=decimal.Decimal("0"),
    )

    class Meta:
        model = Wallet
        fields = ["uuid", "balance"]
