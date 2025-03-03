from locust import HttpUser, task, between


class LoadTestUser(HttpUser):
    wait_time = between(1, 5)
    wallet_uuid = "3f20d7cb-aa10-4a33-a919-3c517decc025"

    @task
    def test_wallet_list(self):
        self.client.get("/api/v1/wallets/")

    # @task
    # def test_wallet_detail(self):
    #     self.client.get(f"/api/v1/wallets/{self.wallet_uuid}/")

    # @task
    # def test_operation_deposit(self):
    #     self.client.post(
    #         f"/api/v1/wallets/{self.wallet_uuid}/operation/",
    #         data={"operationType": "DEPOSIT", "amount": 1},
    #     )
