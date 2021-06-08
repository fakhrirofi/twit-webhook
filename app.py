from dotenv import load_dotenv
from pprint import pprint
from webhook import Event
import os
import json

load_dotenv(".env")

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

server = Event("callback", webhook, process_data)
app = server.get_wsgi()
