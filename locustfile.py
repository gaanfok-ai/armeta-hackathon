from locust import HttpUser, task, between

class LoadTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def upload_pdf(self):
        with open("document.pdf", "rb") as f:
            self.client.post(
                "/predict_json",
                files={"file": ("document.pdf", f, "application/pdf")}
            )
