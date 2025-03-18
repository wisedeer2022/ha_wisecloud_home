from typing import Any

from homeassistant.components.application_credentials import AuthImplementation, ClientCredential, AuthorizationServer
from homeassistant.core import HomeAssistant


class OAuthImpl(AuthImplementation):

    def __init__(
            self,
            hass: HomeAssistant,
            domain: str,
            client_credential: ClientCredential,
            authorization_server: AuthorizationServer,
    ) -> None:
        """Set up Electric Kiwi oauth."""
        super().__init__(
            hass=hass,
            auth_domain=domain,
            credential=client_credential,
            authorization_server=authorization_server,
        )

        self._name = client_credential.name


    async def async_resolve_external_data(self, external_data: Any) -> dict:
        data = await self._token_request(
            {
                "grant_type": "authorization_code",
                "code": external_data["code"],
                "redirect_uri": external_data["state"]["redirect_uri"],
            }
        )
        return data["data"]
