from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "currency_balances" ALTER COLUMN "balance" TYPE DOUBLE PRECISION USING "balance"::DOUBLE PRECISION;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "currency_balances" ALTER COLUMN "balance" TYPE INT USING "balance"::INT;"""
