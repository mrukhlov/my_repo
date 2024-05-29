from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transactions" ALTER COLUMN "transaction_type" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transactions" ALTER COLUMN "transaction_type" SET NOT NULL;"""
