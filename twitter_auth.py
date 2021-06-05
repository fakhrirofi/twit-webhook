from tweepy import OAuthHandler, API
import oauth2
import urllib


def get_xauth_access_token(consumer_key: str, consumer_secret: str,
        username: str, password: str) -> dict:
    # Ref: https://gist.github.com/codingjester/3497868
    '''
    :return: dict of access_token and access_token_secret
    '''
    acces_token_url = 'https://api.twitter.com/oauth/access_token'
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    client = oauth2.Client(consumer)
    client.add_credentials(username, password)
    client.set_signature_method = oauth2.SignatureMethod_HMAC_SHA1()

    resp, token = client.request(
        acces_token_url,
        method="POST",
        body=urllib.parse.urlencode({
            'x_auth_username'   : username,
            'x_auth_password'   : password,
            'x_auth_mode'       : 'client_auth'
        })
    )
    token = dict(urllib.parse.parse_qsl(token.decode()))
    if 'oauth_token' not in token:
        raise Exception("Invalid credentials!")
    return dict(
        access_token=token['oauth_token'],
        access_token_secret=token['oauth_token_secret']
    )

def verify_credentials(consumer_key: str, consumer_secret: str,
        access_token: str, access_token_secret: str):
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    return api.verify_credentials()

class TwitterOAuth:

    def __init__(self, consumer_key: str, consumer_secret: str):
        self._auth = OAuthHandler(consumer_key, consumer_secret)

    def get_url(self) -> str:
        '''Get url to authorize the application
        :return: url
        '''
        return self._auth.get_authorization_url()
    
    def get_token(self, verifier: str) -> dict:
        '''
        :param verifier: PIN
        :return: dict of access_token and access_token_secret
        '''
        data = self._auth.get_access_token(str(verifier))
        return dict(
            access_token=data[0],
            access_token_secret=data[1]
        )
        