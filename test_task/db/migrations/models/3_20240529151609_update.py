from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "equipment" ADD "slot" VARCHAR(6) NOT NULL;
        ALTER TABLE "equipment" ADD "equipped" BOOL NOT NULL  DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "equipment" DROP COLUMN "slot";
        ALTER TABLE "equipment" DROP COLUMN "equipped";"""
