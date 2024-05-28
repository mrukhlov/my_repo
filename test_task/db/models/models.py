from tortoise import fields
from tortoise.models import Model

from test_task.db.mixins import TimestampMixin


class User(Model, TimestampMixin):
    """User model."""

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)

    characters: fields.ReverseRelation["Character"]
    profile: fields.ReverseRelation["UserProfile"]

    class Meta:
        table = "users"
        orm_mode = True


class Character(Model, TimestampMixin):
    """Character model."""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="characters",
    )
    level = fields.IntField(default=1)
    experience = fields.IntField(default=0)

    equipment: fields.ReverseRelation["Equipment"]
    currency_balance: fields.ReverseRelation["CurrencyBalance"]
    inventory: fields.ReverseRelation["Inventory"]
    transaction_from: fields.ReverseRelation["Transaction"]
    transactiony: fields.ReverseRelation["Transaction"]

    class Meta:
        table = "characters"
        orm_mode = True


class Equipment(Model, TimestampMixin):
    """Equipment model."""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    type = fields.CharField(max_length=50)  # e.g., "armor", "weapon"
    character: fields.ForeignKeyRelation[Character] = fields.ForeignKeyField(
        "models.Character",
        related_name="equipment",
    )
    power = fields.IntField(default=0)

    transactions: fields.ReverseRelation["Transaction"]

    class Meta:
        table = "equipment"
        orm_mode = True


class UserProfile(Model, TimestampMixin):
    """User profile model."""

    id = fields.IntField(pk=True)
    user: fields.OneToOneRelation[User] = fields.OneToOneField(
        "models.User",
        related_name="profile",
    )
    bio = fields.TextField(null=True, blank=True)
    avatar_url = fields.CharField(max_length=255, null=True, blank=True)
    location = fields.CharField(max_length=255, null=True, blank=True)

    class Meta:
        table = "user_profiles"
        orm_mode = True


class CurrencyType(Model, TimestampMixin):
    """Currency type model."""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)  # e.g., "gold", "gems"
    description = fields.TextField(null=True, blank=True)

    transactions: fields.ReverseRelation["Transaction"]
    currency_balances: fields.ReverseRelation["CurrencyBalance"]

    class Meta:
        table = "currency_types"
        orm_mode = True


class CurrencyBalance(Model, TimestampMixin):
    """Currency model."""

    id = fields.IntField(pk=True)
    character: fields.ForeignKeyRelation[Character] = fields.ForeignKeyField(
        "models.Character",
        related_name="balances",
    )
    currency_type: fields.ForeignKeyRelation[CurrencyType] = fields.ForeignKeyField(
        "models.CurrencyType",
        related_name="balances",
    )
    balance = fields.IntField(default=0)

    transactions: fields.ReverseRelation["Transaction"]

    class Meta:
        table = "currency_balances"
        orm_mode = True


class Transaction(Model, TimestampMixin):
    """Transaction model."""

    id = fields.IntField(pk=True)
    transaction_type = fields.CharField(max_length=50)  # e.g., "purchase", "sale"
    amount = fields.IntField()
    item: fields.ForeignKeyRelation[Equipment] = fields.ForeignKeyField(
        "models.Equipment",
        related_name="transactions",
    )
    currency_type: fields.ForeignKeyRelation[CurrencyType] = fields.ForeignKeyField(
        "models.CurrencyType",
        related_name="transactions",
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    character_from: fields.ForeignKeyRelation[Character] = fields.ForeignKeyField(
        "models.Character",
        related_name="transactions_from",
    )
    character_to: fields.ForeignKeyRelation[Character] = fields.ForeignKeyField(
        "models.Character",
        related_name="transactions_to",
    )

    class Meta:
        table = "transactions"
        orm_mode = True


class Inventory(Model, TimestampMixin):
    """Inventory model."""

    id = fields.IntField(pk=True)
    character: fields.ForeignKeyRelation[Character] = fields.ForeignKeyField(
        "models.Character",
        related_name="inventory",
    )
    item_name = fields.CharField(max_length=255)
    item_type = fields.CharField(max_length=50)  # e.g., "potion", "scroll"
    quantity = fields.IntField(default=1)

    class Meta:
        table = "inventory"
        orm_mode = True
