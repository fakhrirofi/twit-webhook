from dotenv import load_dotenv
from pyngrok import ngrok
from threading import Thread
from time import sleep
from twitivity import Activity
from webhook import Event
import os

load_dotenv("test.env")


class TestTwitivity:
    URL: str = None
    webhook_id: str = None
    reg = Activity(
        os.environ["CONSUMER_KEY"],
        os.environ["CONSUMER_SECRET"],
        os.environ["ACCESS_TOKEN"],
        os.environ["ACCESS_TOKEN_SECRET"],
        os.environ["ENV_NAME"],
    )

    @classmethod
    def start_webhook(cls):
        http = ngrok.connect(8080, bind_tls=True)
        cls.URL = http.public_url

        def callable(data):
            assert isinstance(data, dict)

        webhook = {
            "testing": {
                "consumer_secret": os.environ["CONSUMER_SECRET"],
                "subscriptions": [{"user_id": "123456789", "callable": callable}],
            }
        }

        server = Event("callback", webhook)
        app = server.get_wsgi()
        t = Thread(target=app.run, kwargs={"port": 8080})
        t.daemon = True
        t.start()
        sleep(0.5)

    @classmethod
    def set_webhook_id(cls, webhook_id):
        cls.webhook_id = webhook_id

    def test_delete_all_webhook(self):
        self.start_webhook()
        self.reg.delete_all()
        # webhooks method is called inside delete_all method

    def test_register_webhook(self):
        response = self.reg.register_webhook(f"{self.URL}/callback/testing")
        self.set_webhook_id(response["id"])

    def test_subscribe_webhook(self):
        self.reg.subscribe()

    def test_refresh(self):
        self.reg.refresh(self.webhook_id)
        ngrok.kill()
