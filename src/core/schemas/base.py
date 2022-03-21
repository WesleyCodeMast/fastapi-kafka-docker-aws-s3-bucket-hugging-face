from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


__all__ = (
    'BaseSchema',
)
