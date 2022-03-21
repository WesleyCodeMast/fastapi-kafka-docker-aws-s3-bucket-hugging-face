class AdaptyError(Exception):
    pass


class AdaptyUnreachable(AdaptyError):
    pass


__all__ = (
    'AdaptyError',
    'AdaptyUnreachable',
)
