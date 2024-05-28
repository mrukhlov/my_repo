from tortoise import fields


class TimestampMixin:
    """Timestamp mixin."""

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
