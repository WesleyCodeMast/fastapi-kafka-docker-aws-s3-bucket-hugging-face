from confluent_kafka import Producer, Consumer
from pydantic.errors import PydanticUserError

from core.db import get_session_maker
from core.settings import get_application_settings

from media.models import Media

from .schemas import ImageTask, ImageResult
from .exceptions import KafkaError

from functools import lru_cache

from loguru import logger

import time, os


@lru_cache
def get_kafka_producer() -> Producer:
    settings = get_application_settings()

    return Producer({
        'bootstrap.servers': settings.KAFKA_SERVICE,
        'group.id': 'sd-backend',
    })


def get_kafka_consumer(topic: str) -> Consumer:
    settings = get_application_settings()

    consumer = Consumer({
        'bootstrap.servers': settings.KAFKA_SERVICE,
        'auto.offset.reset': 'earliest',
        'group.id': f'sd-backend-{os.getpid()}',
    })

    consumer.subscribe([topic])

    return consumer


def send_generation_task(task_id: int, model: str, prompt: str, gender: str, age: str, images_count: int) -> ImageTask:
    """
    Produce image generation task to the kafka

    :param task_id: Task identifier
    :param model: Model name
    :param prompt: Prompt name
    :param gender: Gender (like male, female etc.)
    :param age: Age range (string like "20-24")
    :param images_count: Count of images for generation
    :return: Image generation task object
    """

    image_task = ImageTask(
        id=task_id,
        model=model,
        prompt=prompt,
        gender=gender,
        age=age,
        images_count=images_count,
    )

    producer = get_kafka_producer()
    producer.produce('sd-tasks', value=image_task.model_dump_json())

    logger.info(f'Produced image generation task: {image_task=}')

    return image_task


async def get_generated_images(task_id: int, timeout: int = 180) -> list[Media]:
    """
    Wait kafka for generation response

    :param task_id: Task identifier
    :param timeout: Wait timeout
    :return: List of media objects
    """

    consumer = get_kafka_consumer('sd-results')
    now = time.time()
    result = None

    while time.time() - now <= timeout:
        message = consumer.poll(timeout=1)

        if message is None:
            continue

        if message.error():
            logger.error(f'Kafka message error: {str(message.error())}')
            continue

        value = message.value().decode('utf-8')

        logger.info(f'Got message from kafka: {value=}')

        try:
            result = ImageResult.model_validate_json(value)
        except PydanticUserError:
            logger.error(f'Can\'t get image result value from: {value=}')
            continue

        if result.id != task_id:
            continue

        break

    consumer.close()

    if not result or result.status != 'success' or not result.images:
        logger.error(f'Error on the kafka result: {result=}')
        raise KafkaError(detail=result.message if result and result.message else 'The queue did not respond')

    session = get_session_maker()
    settings = get_application_settings()
    media_list = []

    for image in result.images:
        file_name = image.split('/')[-1]
        full_path = settings.S3_STORAGE_URL + image

        media = Media(name=file_name, url=full_path)
        media_list.append(media)

        session.add(media)

    await session.commit()
    await session.close()

    return media_list


__all__ = (
    'send_generation_task',
    'get_generated_images',
)
