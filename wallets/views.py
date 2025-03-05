import decimal

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from wallets.serializers import WalletSerializer
from wallets.models import Wallet


class WalletList(generics.ListCreateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class WalletDetail(generics.RetrieveAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    lookup_field = "uuid"


class WalletOperation(APIView):
    def post(self, request, uuid):
        try:
            wallet = Wallet.objects.get(uuid=uuid)
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet does not exist."}, status=status.HTTP_404_NOT_FOUND
            )

        operation_type = request.data.get("operationType")
        amount = request.data.get("amount")

        if operation_type is None or amount is None:
            return Response(
                {"error": "operationType and amount must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = decimal.Decimal(amount).quantize(decimal.Decimal(".01"))
        except decimal.InvalidOperation:
            return Response(
                {"error": "amount value is invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if amount < 0:
            return Response(
                {"error": "amount cannot be negative."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if operation_type == "DEPOSIT":
            wallet.deposit(amount)

        elif operation_type == "WITHDRAW":
            try:
                wallet.withdraw(amount)
            except ValueError:
                return Response(
                    {"error": "Not enough money."}, status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {"error": "Wrong operation type, must be either DEPOSIT or WITHDRAW."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(WalletSerializer(wallet).data, status=status.HTTP_200_OK)
