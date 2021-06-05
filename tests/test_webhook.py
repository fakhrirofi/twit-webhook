from threading import Thread
from time import sleep
from webhook import Event
import requests

import hmac
import hashlib
import base64

class TestTwitivity:
    webhook: dict = None

    def create_signature(self, key, msg, digest=hashlib.sha256):
        hash_digest = hmac.digest(
            key=key,
            msg=msg,
            digest=digest
        )
        return base64.b64encode(hash_digest).decode('ascii')

    @classmethod
    def start_webhook(cls):
        def callable(data):
            assert isinstance(data, dict)

        cls.webhook = {
            'testing': {
                'consumer_secret': 'CONSUMER_SECRET',
                'subscriptions': [
                    {
                    'user_id': '123456789',
                    'callable': callable
                    }
                ]
            }
        }


        server = Event('callback', cls.webhook)
        app = server.get_wsgi()
        t = Thread(target=app.run, kwargs={'port': 4040})
        t.daemon = True
        t.start()
        sleep(0.5)

    def test_receive_get(self):
        self.start_webhook()
        crc_token = 'randomj4d1d7fape8ce82b7d8c'
        r = requests.get(f'http://127.0.0.1:4040/callback/testing?crc_token={crc_token}')
        assert r.status_code == 200
        signature = self.create_signature(
            self.webhook['testing']['consumer_secret'].encode('utf-8'),
            crc_token.encode('utf-8'))
        assert r.json()['response_token'] == f"sha256={signature}"

    def test_receive_put(self):
        crc_token = 'randomj4d1d7fape8ce82b7d8c'
        r = requests.put(f'http://127.0.0.1:4040/callback/testing?crc_token={crc_token}')
        assert r.status_code == 200
        signature = self.create_signature(
            self.webhook['testing']['consumer_secret'].encode('utf-8'),
            crc_token.encode('utf-8'))
        assert r.json()['response_token'] == f"sha256={signature}"

    def test_receive_post(self):
        signature = self.create_signature(
            self.webhook['testing']['consumer_secret'].encode('utf-8'),
            '{"for_user_id": "123456789", "test": "test"}'.encode('utf-8'),
        )
        r = requests.post('http://127.0.0.1:4040/callback/testing',
            json={"for_user_id": "123456789", "test": "test"},
            headers={"X-Twitter-Webhooks-Signature": f"sha256={signature}"})
        assert r.status_code == 200

    def test_receive_wrong_post(self):
        # no headers
        r = requests.post('http://127.0.0.1:4040/callback/testing',
            json={"for_user_id": "123456789", "test": "test"})
        assert r.status_code == 403

        # wrong signature
        r = requests.post('http://127.0.0.1:4040/callback/testing',
            json={"for_user_id": "123456789", "test": "test"},
            headers={"X-Twitter-Webhooks-Signature": f"sha256=h7dghe7w9dgfi73ga7"})
        assert r.status_code == 403

        # wrong user id
        signature = self.create_signature(
            self.webhook['testing']['consumer_secret'].encode('utf-8'),
            '{"for_user_id": "123456789123456789", "test": "test"}'.encode('utf-8'),
        )
        r = requests.post('http://127.0.0.1:4040/callback/testing',
            json={"for_user_id": "123456789123456789", "test": "test"},
            headers={"X-Twitter-Webhooks-Signature": f"sha256={signature}"})
        assert r.status_code == 404

    def test_wrong_webhook_route(self):
        r = requests.post('http://127.0.0.1:4040/callback/haha')
        assert r.status_code == 404

