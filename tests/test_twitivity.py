from dotenv import load_dotenv
from pyngrok import ngrok
from threading import Thread
from time import sleep
from twitivity import Activity
from webhook import Event
import os

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