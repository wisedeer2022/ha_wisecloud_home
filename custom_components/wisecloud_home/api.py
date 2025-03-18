"""API for 云鹿云oauth2测试 bound to Home Assistant OAuth."""
from abc import ABC

from aiohttp import ClientSession, ClientResponse

from homeassistant.helpers import config_entry_oauth2_flow
from .const import API_BASE_URL


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


    async def request(self, method, url, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")
        if headers is None:
            headers = {}
        else:
            headers = dict(headers)
        access_token = await self.async_get_access_token()
        headers["authorization"] = f"Bearer {access_token}"
        response = await self._websession.request(
            method, f"{API_BASE_URL}/{url}", **kwargs, headers=headers,
        )
        respJson = await response.json()
        # 判断响应状态码
        if respJson["code"] != 200:
            raise Exception(respJson["msg"])

        return respJson["data"]