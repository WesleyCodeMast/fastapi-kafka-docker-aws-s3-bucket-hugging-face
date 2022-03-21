from core.schemas import BaseSchema


class ImageTask(BaseSchema):
    """ Schema of image generation task """

    id: int
    model: str
    prompt: str
    gender: str
    age: str
    images_count: int


class ImageAttemptInfo(BaseSchema):
    """ Schema of information about generation attempt """

    attempt: int
    last_attempt_error: str


class ImageResult(ImageTask):
    """ Schema of image generation result """

    info: ImageAttemptInfo
    images: list[str]
    status: str
    message: str


__all__ = (
    'ImageTask',
    'ImageAttemptInfo',
    'ImageResult',
)
