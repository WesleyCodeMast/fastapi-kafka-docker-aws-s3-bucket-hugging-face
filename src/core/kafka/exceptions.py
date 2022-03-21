from core.exceptions import APIError


class KafkaError(APIError):
    status_code = 400
    code = 'queue.error'


__all__ = (
    'KafkaError',
)
