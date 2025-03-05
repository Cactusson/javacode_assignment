import uuid

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from wallets.models import Wallet


class TestWalletList(APITestCase):
    def setUp(self):
        self.url = reverse("wallet-list")

    def test_status_code(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_wallet_status_code(self):
        response = self.client.post(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_wallet_balance_is_zero_by_default(self):
        response = self.client.post(self.url, format="json")
        self.assertEqual(response.json()["balance"], "0.00")

    def test_create_wallet_balance_is_positive(self):
        response = self.client.post(self.url, {"balance": 100}, format="json")
        self.assertEqual(response.json()["balance"], "100.00")

    def test_create_wallet_balance_is_negative(self):
        response = self.client.post(self.url, {"balance": -100}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wallet_invalid_balance(self):
        response = self.client.post(self.url, {"balance": "---"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_wallet_appears_in_the_list(self):
        self.client.get(self.url)
        response = self.client.post(self.url, {"balance": 100}, format="json")
        uuid, balance = response.json()['uuid'], response.json()['balance']
        response = self.client.get(self.url, format="json").json()
        self.assertIn({'uuid': uuid, 'balance': balance}, response)


class TestWalletDetail(APITestCase):
    def test_wallet_does_not_exist(self):
        url = reverse("wallet-detail", kwargs={"uuid": uuid.uuid4()})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wallet_exists(self):
        wallet = Wallet.objects.create()
        url = reverse("wallet-detail", kwargs={"uuid": wallet.uuid})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_balance_is_zero(self):
        wallet = Wallet.objects.create()
        url = reverse("wallet-detail", kwargs={"uuid": wallet.uuid})
        response = self.client.get(url, format="json")
        self.assertEqual(response.json()["balance"], "0.00")

    def test_balance_is_not_zero(self):
        wallet = Wallet.objects.create(balance=100)
        url = reverse("wallet-detail", kwargs={"uuid": wallet.uuid})
        response = self.client.get(url, format="json")
        self.assertEqual(response.json()["balance"], "100.00")


class TestOperation(APITestCase):
    def setUp(self):
        self.empty_wallet = Wallet.objects.create()
        self.full_wallet = Wallet.objects.create(balance=1000)

    def make_request(self, uuid, data):
        url = reverse("wallet-operation", kwargs={"uuid": uuid})
        return self.client.post(url, data, format="json")

    def test_empty_json(self):
        response = self.make_request(self.empty_wallet.uuid, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_operation_type_is_not_provided(self):
        response = self.make_request(self.empty_wallet.uuid, {"amount": "10"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_amount_is_not_provided(self):
        response = self.make_request(
            self.empty_wallet.uuid, {"operationType": "DEPOSIT"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_amount_is_invalid(self):
        response = self.make_request(
            self.empty_wallet.uuid, {"operationType": "DEPOSIT", "amount": "---"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wallet_does_not_exist(self):
        response = self.make_request(
            uuid.uuid4(), {"operationType": "DEPOSIT", "amount": "100"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_operation_type(self):
        response = self.make_request(
            self.empty_wallet.uuid, {"operationType": "---", "amount": "100"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_amount_is_negative(self):
        response = self.make_request(
            self.empty_wallet.uuid, {"operationType": "DEPOSIT", "amount": "-100"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_enough_money(self):
        response = self.make_request(
            self.empty_wallet.uuid, {"operationType": "WITHDRAW", "amount": "100"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deposit_successful_status_code(self):
        response = self.make_request(
            self.empty_wallet.uuid, {"operationType": "DEPOSIT", "amount": "100"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deposit_successful_balance_is_right(self):
        self.make_request(
            self.empty_wallet.uuid, {"operationType": "DEPOSIT", "amount": "100"}
        )
        self.empty_wallet.refresh_from_db()
        self.assertEqual(self.empty_wallet.balance, 100)

    def test_withdraw_successful_status_code(self):
        response = self.make_request(
            self.full_wallet.uuid, {"operationType": "WITHDRAW", "amount": "100"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_withdraw_successful_balance_is_right(self):
        self.make_request(
            self.full_wallet.uuid, {"operationType": "WITHDRAW", "amount": "100"}
        )
        self.full_wallet.refresh_from_db()
        self.assertEqual(self.full_wallet.balance, 900)

    def test_balance_has_changed(self):
        wallet = Wallet.objects.create(balance=100)
        url = reverse("wallet-detail", kwargs={"uuid": wallet.uuid})
        self.client.get(url, format="json").json()
        self.make_request(wallet.uuid, {"operationType": "DEPOSIT", "amount": "100"})
        response = self.client.get(url, format="json")
        self.assertEqual(response.json()['balance'], "200.00")
