from aiohttp import ClientSession, TCPConnector
from aiohttp.client_exceptions import ClientError, ContentTypeError

from .schemas import AdaptyProfile
from .exceptions import AdaptyUnreachable

import json, ssl, certifi


class AdaptyClient:
    _base_url = 'https://api.adapty.io/api/v1/sdk'
    _secret_key: str
    _session: ClientSession = None

    def __init__(self, secret_key: str) -> None:
        """
        The Adapty client for working with the API and
        receiving information from the Adapty servers

        :param secret_key: API secret token
        """

        self._secret_key = secret_key

    async def get_profile(self, user_id: str) -> AdaptyProfile:
        """
        Retrieves information about a user by their id

        :param user_id: User identifier
        :type user_id: str
        :return: Adapty profile schema
        """

        return AdaptyProfile.model_validate((await self(endpoint=f'profiles/{user_id}')).get('data', {}))

    async def _get_session(self) -> 'ClientSession':
        """
        Gets a new session to complete the request

        :return: Aiohttp client session
        """

        if not self._session or self._session.closed:
            self._session = self._create_session()

        return self._session

    def _build_url(self, endpoint: str) -> str:
        """
        Collects the full address for the connection

        :param endpoint: The method being called to get the data
        :return: Url address
        """

        base_url = self._base_url

        if base_url.endswith('/'):
            base_url = base_url[:-1]

        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint

        if not endpoint.endswith('/'):
            endpoint += '/'

        return base_url + endpoint

    @property
    def _headers(self) -> dict[str, str]:
        return {
            'Authorization': f'Api-Key {self._secret_key}',
        }

    @staticmethod
    def _create_session() -> 'ClientSession':
        """
        Creates a new session to connect to

        :return: Aiohttp client session
        """

        return ClientSession(
            connector=TCPConnector(ssl=ssl.create_default_context(cafile=certifi.where())),
            json_serialize=json.dumps,
        )

    async def __call__(self, endpoint: str) -> dict:
        """
        Executes a request to the Adapty servers

        :param endpoint: The method being called to get the data
        :return: Response from the Adapty server
        """

        url = self._build_url(endpoint)
        session = await self._get_session()

        try:
            async with session.get(url=url, headers=self._headers) as response:
                try:
                    result = await response.json()
                except ContentTypeError:
                    result = await response.text()
        except ClientError:
            raise AdaptyUnreachable()

        return result


__all__ = (
    'AdaptyClient',
)
