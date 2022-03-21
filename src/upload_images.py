from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from core.db import get_session_maker
from core.settings import get_application_settings
from core.events import on_startup_handler, on_shutdown_handler

from avatars.models import Avatar

from media.models import Media
from media.services import store_photo

import os, asyncio


async def upload_media() -> None:
    """ Upload media to the avatars """

    settings = get_application_settings()

    await on_startup_handler(settings)

    session = get_session_maker()

    for root, dirs, files in os.walk('static'):
        dir_name = root.split(os.path.sep)[-1]

        if not dir_name.isdigit():
            continue

        statement = select(Avatar).where(Avatar.id == int(dir_name)).options(selectinload(Avatar.message_photo))
        query = await session.execute(statement)

        avatar: Avatar = query.scalar_one_or_none()

        if not avatar:
            continue

        avatar.message_photo[:] = []

        for file_name in files:
            full_path = root + os.path.sep + file_name

            photo = await store_photo(file=full_path)

            avatar.message_photo.append(photo)

            session.add(avatar)

            await asyncio.sleep(1.05)

        await session.commit()

    await on_shutdown_handler(settings)


asyncio.run(upload_media())
