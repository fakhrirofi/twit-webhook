from flask import Flask, request
from typing import TypedDict, Callable, List, NoReturn, Optional
import hmac
import hashlib
import logging
import base64
import json

logger = logging.getLogger(__name__)

class DictWebhook(TypedDict):
    user_id: str
    consumer_secret: Optional[str]
    function: Callable[[dict], NoReturn]

class Event:

    def __init__(self, callback_route: str, webhook: List[DictWebhook]):
        '''
        :param callback_route: flask wsgi route without slash '/'
        :param webhook: list of webhook dictionary that contains the following keys:\
            user_id, consumer_secret (optional), and function
        '''
        self.callback_route: str = callback_route
        self.webhook: List[DictWebhook] = webhook

    def get_wsgi(self) -> Flask:
        # Ref: https://github.com/twitivity/twitivity
        '''Get Flask WSGI app
        :return: Flask WSGI app
        '''
        app = Flask(__name__)
        @app.route(f'/{self.callback_route}/<user_id>', methods=['GET', 'POST', 'PUT'])
        def callback(user_id: str) -> json:
            if request.method == 'GET' or request.method == 'PUT':
                webhook = list(filter(lambda x: x['user_id'] == user_id, self.webhook))
                try:
                    assert webhook
                except Exception:
                    logger.error('user_id not found')
                    return {"code": 404}, 404
                hash_digest = hmac.digest(
                    key=webhook[0]['consumer_secret'].encode('utf-8'),
                    msg=request.args.get('crc_token').encode('utf-8'),
                    digest=hashlib.sha256,
                )
                return {
                    "response_token": "sha256="
                    + base64.b64encode(hash_digest).decode("ascii")
                }

            elif request.method == 'POST':
                data = request.get_json()
                webhook = list(filter(lambda x: x['user_id'] == user_id, self.webhook))
                try:
                    assert webhook
                except Exception:
                    logger.error('user_id not found')
                    return {"code": 404}, 404
                webhook[0]['function'](data)
                return {"code": 200}
        
        return app
