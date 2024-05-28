from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
INSERT INTO roles (name, permissions) VALUES ('user', '{}');
INSERT INTO roles (name, permissions) VALUES ('admin', '{}');
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "roles";"""
