"""Application credentials platform for the 云鹿云oauth2测试 integration."""

from homeassistant.components.application_credentials import AuthorizationServer, ClientCredential
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .const import OAUTH2_AUTHORIZE, OAUTH2_TOKEN, OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET, OAUTH2_CLIENT_NAME
from .oauth_impl import OAuthImpl


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    """Return auth implementation."""
    return OAuthImpl(
        hass,
        auth_domain,
        client_credential=await async_get_client_credential(),
        authorization_server=await async_get_authorization_server(hass),
    )

async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server."""
    return AuthorizationServer(
        authorize_url=OAUTH2_AUTHORIZE,
        token_url=OAUTH2_TOKEN,
    )

async def async_get_client_credential():
    """Return client credential."""
    return ClientCredential(
        client_id=OAUTH2_CLIENT_ID,
        client_secret=OAUTH2_CLIENT_SECRET,
        name=OAUTH2_CLIENT_NAME,
    )