from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transactions" ALTER COLUMN "item_id" DROP NOT NULL;
        ALTER TABLE "transactions" ALTER COLUMN "character_from_id" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "transactions" ALTER COLUMN "item_id" SET NOT NULL;
        ALTER TABLE "transactions" ALTER COLUMN "character_from_id" SET NOT NULL;"""
