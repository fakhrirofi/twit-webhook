from dotenv import load_dotenv
from pprint import pprint
from webhook import Event
import os
import json

load_dotenv('.env')

# function that will be called when webhook receives data
def testing(data: json):
    '''
    :param data: Ref: https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/guides/account-activity-data-objects
    '''
    # your code here...
    pprint(data)

webhook = [
    {
        'user_id': os.environ['ACCESS_TOKEN'].split('-')[0],
        'consumer_secret': os.environ['CONSUMER_SECRET'],
        'function': testing,
    },
]

server = Event('callback', webhook)
app = server.get_wsgi()
