from dotenv import load_dotenv
from tools import get_xauth_access_token, verify_credentials
import os

load_dotenv('test.env')

def test_register_xauth():
    if os.environ.get('TWITTER_USERNAME') and os.environ.get('TWITTER_PASSWORD'):
        consumer_key = os.environ['XAUTH_CONSUMER_KEY']
        consumer_secret = os.environ['XAUTH_CONSUMER_SECRET']
        username = os.environ['TWITTER_USERNAME']
        password = os.environ['TWITTER_PASSWORD']
        token = get_xauth_access_token(consumer_key, consumer_secret, username, password)
        verify_credentials(consumer_key, consumer_secret, token['access_key'], token['access_secret'])
