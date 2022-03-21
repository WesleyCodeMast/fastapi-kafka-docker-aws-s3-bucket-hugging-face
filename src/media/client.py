from pydantic import BaseModel

from aiobotocore.session import get_session

from time import time
from io import BytesIO
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiobotocore.session import AioSession, AioBaseClient


class S3Config(BaseModel):
    """ Configuration for connecting and working with object storage """

    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str | None = None
    region_name: str | None = None


class S3Client:
    """ Client for working with S3 storage (object storage) """

    _config: S3Config
    _bucket_name: str
    _session: 'AioSession'

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        endpoint_url: str = None,
        region_name: str = None,
    ) -> None:
        self._config = S3Config(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            region_name=region_name,
        )

        self._bucket_name = bucket_name
        self._session = get_session()

    @asynccontextmanager
    async def get_client(self) -> 'AioBaseClient':
        async with self._session.create_client('s3', **self._config.model_dump()) as client:
            yield client

    async def upload_file(self, file: BytesIO | str, extension: str = None):
        if isinstance(file, BytesIO) and not extension:
            raise AttributeError('The extension is required if a link to the file is not passed')

        extension = extension or file.split('.')[-1]
        file_name = f'photo_{int(time())}.{extension}'

        async with self.get_client() as client:
            client: 'AioBaseClient' = client
            file_read = False

            if isinstance(file, str):
                file_read = True
                file_instance = open(file, 'rb')
            else:
                file_instance = file

            await client.put_object(
                Bucket=self._bucket_name,
                Key=file_name,
                Body=file_instance,
            )

            if file_read is True:
                file_instance.close()

        return file_name


__all__ = (
    'S3Client',
)
