from flask import Flask, request
from typing import Dict
from validators import url as validate_url
import hmac
import hashlib
import logging
import base64
import json

logger = logging.getLogger(__name__)


class Event:
    def __init__(self, callback_route: str, webhook: Dict[str, str], on_data):
        """
        :param callback_route: flask wsgi route without slash '/'
        :param webhook: dictionary, name of the webhook is the key and consumer secret is the value.
            {"name_of_the_webhook": "CONSUMER_SECRET"}
        :param on_data: callable that will be called when webhook receives data.
        """
        if not validate_url(f"https://testing.com/{callback_route}"):
            raise ValueError(f"The callback_route '{callback_route}' is invalid")
        if "/" in callback_route:
            raise ValueError(
                f"The callback_route '{callback_route}' doesn't need slash '/'"
            )
        self.callback_route: str = callback_route

        for x in list(webhook):
            if not validate_url(f"https://testing.com/{x}"):
                raise ValueError(f"The webhook_name '{x}' is invalid")
        self.webhook: Dict[str, str] = webhook
        self.on_data = on_data

    @staticmethod
    def create_signature(consumer_secret: str, crc_token: str) -> str:
        hash_digest = hmac.digest(
            key=consumer_secret.encode("utf-8"),
            msg=crc_token.encode("utf-8"),
            digest=hashlib.sha256,
        )
        return base64.b64encode(hash_digest).decode("ascii")

    @staticmethod
    def verify_request(
        consumer_secret: str, request_headers: dict, request_data: bytes
    ) -> bool:
        try:
            signature = request_headers["X-Twitter-Webhooks-Signature"][7:]
            hash_digest = hmac.digest(
                key=consumer_secret.encode("utf-8"),
                msg=request_data,
                digest=hashlib.sha256,
            )
            return hmac.compare_digest(
                signature, base64.b64encode(hash_digest).decode("ascii")
            )
        except Exception:
            return False

    def get_wsgi(self) -> Flask:
        # Ref: https://github.com/twitivity/twitivity
        """Get Flask WSGI app
        :return: Flask WSGI app
        """
        app = Flask(__name__)

        @app.route(
            f"/{self.callback_route}/<webhook_name>", methods=["GET", "POST", "PUT"]
        )
        def callback(webhook_name: str) -> json:
            if webhook_name not in self.webhook:
                logger.error("Webhook name not found")
                return {"code": 404}, 404

            if request.method == "GET" or request.method == "PUT":
                signature = self.create_signature(
                    self.webhook[webhook_name], request.args.get("crc_token")
                )
                return {"response_token": f"sha256={signature}"}

            elif request.method == "POST":
                if not self.verify_request(
                    self.webhook[webhook_name], request.headers, request.get_data()
                ):
                    logger.error("Invalid request signature")
                    return {"code": 403}, 403

                self.on_data(request.get_json())
                return {"code": 200}

        return app
