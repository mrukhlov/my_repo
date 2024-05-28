from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "roles" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "permissions" JSONB NOT NULL
);
COMMENT ON TABLE "roles" IS 'Role model.';
        CREATE TABLE IF NOT EXISTS "users" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "is_verified" BOOL NOT NULL  DEFAULT False,
    "role_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "users" IS 'User model.';
        CREATE TABLE IF NOT EXISTS "characters" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "level" INT NOT NULL  DEFAULT 1,
    "experience" INT NOT NULL  DEFAULT 0,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "characters" IS 'Character model.';
        CREATE TABLE IF NOT EXISTS "currency_types" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "description" TEXT
);
COMMENT ON TABLE "currency_types" IS 'Currency type model.';
        CREATE TABLE IF NOT EXISTS "currency_balances" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "balance" INT NOT NULL  DEFAULT 0,
    "character_id" INT NOT NULL REFERENCES "characters" ("id") ON DELETE CASCADE,
    "currency_type_id" INT NOT NULL REFERENCES "currency_types" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "currency_balances" IS 'Currency model.';
        CREATE TABLE IF NOT EXISTS "equipment" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "type" VARCHAR(50) NOT NULL,
    "power" INT NOT NULL  DEFAULT 0,
    "character_id" INT NOT NULL REFERENCES "characters" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "equipment" IS 'Equipment model.';
        CREATE TABLE IF NOT EXISTS "inventory" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "item_name" VARCHAR(255) NOT NULL,
    "item_type" VARCHAR(50) NOT NULL,
    "quantity" INT NOT NULL  DEFAULT 1,
    "character_id" INT NOT NULL REFERENCES "characters" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "inventory" IS 'Inventory model.';
        CREATE TABLE IF NOT EXISTS "transactions" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "transaction_type" VARCHAR(50) NOT NULL,
    "amount" INT NOT NULL,
    "character_from_id" INT NOT NULL REFERENCES "characters" ("id") ON DELETE CASCADE,
    "character_to_id" INT NOT NULL REFERENCES "characters" ("id") ON DELETE CASCADE,
    "currency_type_id" INT NOT NULL REFERENCES "currency_types" ("id") ON DELETE CASCADE,
    "item_id" INT NOT NULL REFERENCES "equipment" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "transactions" IS 'Transaction model.';
        CREATE TABLE IF NOT EXISTS "user_profiles" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "bio" TEXT,
    "avatar_url" VARCHAR(255),
    "location" VARCHAR(255),
    "user_id" INT NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "user_profiles" IS 'User profile model.';
        DROP TABLE IF EXISTS "dummymodel";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "characters";
        DROP TABLE IF EXISTS "currency_balances";
        DROP TABLE IF EXISTS "currency_types";
        DROP TABLE IF EXISTS "equipment";
        DROP TABLE IF EXISTS "inventory";
        DROP TABLE IF EXISTS "roles";
        DROP TABLE IF EXISTS "transactions";
        DROP TABLE IF EXISTS "users";
        DROP TABLE IF EXISTS "user_profiles";"""
