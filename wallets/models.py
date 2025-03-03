import uuid

from decimal import Decimal

from django.db import models


class Wallet(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self):
        return f"Wallet {self.uuid} (balance: {self.balance})"

    def deposit(self, amount: Decimal) -> None:
        self.balance += amount
        self.save()

    def withdraw(self, amount: Decimal) -> None:
        if self.balance >= amount:
            self.balance -= amount
            self.save()
        else:
            raise ValueError("Not enough money.")
