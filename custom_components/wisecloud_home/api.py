"""API for 云鹿云oauth2测试 bound to Home Assistant OAuth."""
import random
import string
from abc import ABC

from aiohttp import ClientSession, ClientResponse

from homeassistant.helpers import config_entry_oauth2_flow
from .const import API_BASE_URL, API_SIGN_KEY
import base64
import hashlib
import hmac
import json
import time

class WiseCloudAPI(ABC):

    def __init__(
        self,
        websession: ClientSession,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize 云鹿云oauth2测试 auth."""
        self._websession = websession
        self._oauth_session = oauth_session


    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        await self._oauth_session.async_ensure_token_valid()
        return self._oauth_session.token["access_token"]

    def generate_nonce(self, length=16):
        """
        生成指定长度的随机 nonce 字符串
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))


    async def request(self, method, url, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")
        if headers is None:
            headers = {}
        else:
            headers = dict(headers)
        access_token = await self.async_get_access_token()
        headers["authorization"] = f"Bearer {access_token}"

        timestamp = int(time.time())
        nonce = self.generate_nonce()
        top = f"{method} {url} {timestamp} {nonce}\n".encode()
        json_data = kwargs.get("data")
        body = json.dumps(json_data).encode() if json_data else b''
        data = top + body
        signature = base64.b64encode(hmac.new(API_SIGN_KEY, data, hashlib.sha256).digest())

        headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Timestamp': str(timestamp),
            'Nonce': nonce,
            'Signature': signature.decode()
        })

        kwargs["data"] = json.dumps(json_data)
        response = await self._websession.request(
            method, f"{API_BASE_URL}{url}", **kwargs, headers=headers,
        )
        respJson = await response.json()
        # 判断响应状态码
        if respJson["code"] != 200:
            raise Exception(respJson["msg"])

        return respJson["data"]

