from dotenv import load_dotenv
from pyngrok import ngrok
from threading import Thread
from time import sleep
from twitivity import Activity
from webhook import Event
import os
import requests

load_dotenv('test.env')

http = ngrok.connect(8080, bind_tls=True)
URL = http.public_url

def callable(data):
    assert isinstance(data, dict)

webhook = {
    'testing': {
        'consumer_secret': os.environ['CONSUMER_SECRET'],
        'subcriptions': [
            {
            'user_id': '123456789',
            'callable': callable
            }
        ]
    }
}

server = Event('callback', webhook)
app = server.get_wsgi()
t = Thread(target=app.run, kwargs={'port': 8080})
t.daemon = True
t.start()
sleep(2)

reg = Activity(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'],
               os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'],
               os.environ['ENV_NAME'])

def test_delete_webhook():
    reg.delete_all()

def test_register_webhook():
    reg.register_webhook(f"{URL}/callback/testing")

def test_subscribe_webhook():
    reg.subscribe()

def test_receive_get():
    crc_token = 'randomj4d1d7fape8ce82b7d8c'
    r = requests.get(f'http://127.0.0.1:8080/callback/testing?crc_token={crc_token}')
    assert r.status_code == 200

def test_receive_put():
    crc_token = 'randomj4d1d7fape8ce82b7d8c'
    r = requests.put(f'http://127.0.0.1:8080/callback/testing?crc_token={crc_token}')
    assert r.status_code == 200

def test_receive_post():
    r = requests.post('http://127.0.0.1:8080/callback/testing',
        json={"for_user_id":"123456789", "test":"test"})
    assert r.status_code == 200

def test_wrong_callback_route():
    r = requests.post('http://127.0.0.1:8080/haha')
    assert r.status_code == 404
    r = requests.post('http://127.0.0.1:8080/haha/testing')
    assert r.status_code == 404

def test_wrong_webhook_route():
    r = requests.post('http://127.0.0.1:8080/callback/haha')
    assert r.status_code == 404

