import random

from locust import HttpUser, task, between


class BackendUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.user_id = random.randint(5000,  6000)

    @task
    def get_users(self):
        self.client.get(
            f"/users/{self.user_id}",
            name="/users/[user_id]"
            )