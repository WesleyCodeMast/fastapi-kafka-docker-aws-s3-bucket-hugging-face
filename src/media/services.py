from sqlalchemy import select

from core.db import get_session_maker, get_session
from core.settings import get_application_settings

from .client import S3Client
from .models import Media

from io import BytesIO
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@lru_cache
def get_s3_client() -> S3Client:
    settings = get_application_settings()

    return S3Client(
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY.get_secret_value(),
        endpoint_url=settings.S3_ENDPOINT_URL,
        bucket_name='addop-aiavatar',
    )


async def store_photo(file: BytesIO | str, extension: str = None) -> Media:
    """
    Uploads the file to the storage and saves it

    :param file: File path or instance
    :param extension: File extension
    :return: Saved media model object
    """

    if isinstance(file, BytesIO) and not extension:
        raise AttributeError('The extension is required if a link to the file is not passed')

    client = get_s3_client()
    settings = get_application_settings()

    file_name = await client.upload_file(file=file, extension=extension)
    full_path = settings.S3_STORAGE_URL + file_name

    media = Media(name=file_name, url=full_path)
    session = get_session_maker()

    session.add(media)
    await session.commit()
    await session.close()

    return media


async def get_media_by_id(media_id: int, session: 'AsyncSession' = None) -> Media | None:
    """
    Get media content by its identifier

    :param media_id: Media object identifier
    :param session: Database session
    :return: Media model object
    """

    session, is_new_session = get_session(session)

    statement = select(Media).where(Media.id == media_id).limit(1)

    query = await session.execute(statement)

    if is_new_session:
        await session.close()

    return query.scalar_one_or_none()


__all__ = (
    'store_photo',
    'get_media_by_id',
)
