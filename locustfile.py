from locust import HttpLocust, TaskSet, task

class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        self.logout()

    def login(self):
        # self.client.post("/login", {"username":"ellen_key", "password":"education"})
        pass

    def logout(self):
        # self.client.post("/logout", {"username":"ellen_key", "password":"education"})
        pass

    @task(1)
    def index(self):
        self.client.get("/")

    # @task(1)
    # def index(self):
    #     self.client.get("/api/query?code=/kMKKhZC1sFej/3GdWv3HCbK0YRktDdpc2xErkFk4PIewEqsmI6Dgg==")

    # @task(1)
    # def profile(self):
    #     self.client.get("/profile")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 60000
    max_wait = 120000