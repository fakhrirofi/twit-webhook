from dotenv import load_dotenv
from pprint import pprint
from webhook import Event
import os
import json

from threading import Thread
from pyngrok import ngrok
from time import sleep
from twitivity import Activity

load_dotenv(".env")
http = ngrok.connect(8080, bind_tls=True)
URL = http.public_url

# function that will be called when webhook receives data
def process_data(data: json):
    """
    :param data: Ref: https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/guides/account-activity-data-objects
    """
    # your code here...
    pprint(data)


webhook = {
    "name_of_the_webhook": os.environ["CONSUMER_SECRET"],
}

callback_route = "callback"
server = Event(callback_route, webhook, process_data)
app = server.get_wsgi()
Thread(target=app.run, kwargs={"port": 8080}).start()
sleep(3)

reg = Activity(
    os.environ["CONSUMER_KEY"],
    os.environ["CONSUMER_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_TOKEN_SECRET"],
    os.environ["ENV_NAME"],
)
# because we use ngrok (dynamic url) to run the webhook, we should delete all
# webhooks before registering a new webhook url
reg.delete_all()
reg.register_webhook(f"{URL}/{callback_route}/name_of_the_webhook")
reg.subscribe()
