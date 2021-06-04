# Copyright (c) 2019 Saadman Rafat
# Distributed under the MIT software license
# https://github.com/twitivity/twitivity

from typing import NoReturn
from tweepy.error import TweepError
from tweepy import OAuthHandler
import json
import re
import requests


class Activity:
    _protocol: str = "https:/"
    _host: str = "api.twitter.com"
    _version: str = "1.1"
    _product: str = "account_activity"

    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str,
            access_token_secret: str, env_name: str):
        """
        :param consumer_key: Twitter consumer key
        :param consumer_secret: Twitter consumer secret
        :param access_token: Twitter access token
        :param access_token_secret: Twitter access token secret
        :param env_name: Twitter Account Activity API dev environment name
        """
        self._auth: OAuthHandler = OAuthHandler(consumer_key, consumer_secret)
        self._auth.set_access_token(access_token, access_token_secret)
        self.env_name: str = env_name

    def api(self, method: str, endpoint: str, data: dict = None) -> json:
        """
        :param method: GET or POST
        :param endpoint: API Endpoint to be specified by user
        :param data: POST Request payload parameter
        :return: json
        """
        try:
            with requests.Session() as r:
                response = r.request(
                    url="/".join(
                        [
                            self._protocol,
                            self._host,
                            self._version,
                            self._product,
                            endpoint,
                        ]
                    ),
                    method=method,
                    auth=self._auth.apply_auth(),
                    data=data,
                )
                return response
        except TweepError:
            raise

    def register_webhook(self, callback_url: str) -> json:
        try:
            return self.api(
                method="POST",
                endpoint=f"all/{self.env_name}/webhooks.json",
                data={"url": callback_url},
            ).json()
        except Exception as e:
            raise e

    def refresh(self, webhook_id: str) -> NoReturn:
        """Refreshes CRC for the provided webhook_id.
        """
        try:
            return self.api(
                method="PUT",
                endpoint=f"all/{self.env_name}/webhooks/{webhook_id}.json",
            )
        except Exception as e:
            raise e

    def delete(self, webhook_id: str) -> NoReturn:
        """Removes the webhook from the provided webhook_id.
        """
        try:
            return self.api(
                method="DELETE",
                endpoint=f"all/{self.env_name}/webhooks/{webhook_id}.json",
            )
        except Exception as e:
            raise e
    
    def delete_all(self) -> NoReturn:
        """Delete all webhooks
        """
        try:
            for environment in self.webhooks()['environments']:
                if environment['environment_name'] == self.env_name:
                    for webhook in environment['webhooks']:
                        webhook_id = environment['webhooks'][webhook]['id']
                        self.delete(webhook_id)
        except Exception as e:
            raise e

    def subscribe(self) -> NoReturn:
        """Create subscription to the webhook
        """
        try:
            return self.api(
                method="POST",
                endpoint=f"all/{self.env_name}/subscriptions.json",
            )
        except Exception:
            raise

    def webhooks(self) -> json:
        """Returns all environments, webhook URLs and their statuses for the authenticating app.
        Only one webhook URL can be registered to each environment.
        """
        try:
            return self.api(method="GET", endpoint=f"all/webhooks.json").json()
        except Exception as e:
            raise e
