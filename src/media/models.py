from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from core.db.base import BaseModel, TimestampMixin

from typing import TYPE_CHECKING


class Media(BaseModel, TimestampMixin):
    """ Media content stored in S3 storage """

    __tablename__ = 'media'

    if TYPE_CHECKING:
        name: str
        url: str
    else:
        name: Mapped[str] = mapped_column(Text)
        # The name of the saved file

        url: Mapped[str] = mapped_column(Text)
        # The address of the file saved in the repository


__all__ = (
    'Media',
)
