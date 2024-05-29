from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "equipment" ADD "currency_type_id" INT NOT NULL;
        ALTER TABLE "equipment" ADD "price" DOUBLE PRECISION NOT NULL  DEFAULT 0;
        ALTER TABLE "equipment" ADD "quantity" INT NOT NULL  DEFAULT 1;
        CREATE UNIQUE INDEX "uid_currency_ba_charact_4a8294" ON "currency_balances" ("character_id", "currency_type_id");
        CREATE UNIQUE INDEX "uid_equipment_charact_56d09e" ON "equipment" ("character_id", "name");
        ALTER TABLE "equipment" ADD CONSTRAINT "fk_equipmen_currency_1bd4eb18" FOREIGN KEY ("currency_type_id") REFERENCES "currency_types" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "uid_currency_ba_charact_4a8294";
        ALTER TABLE "equipment" DROP CONSTRAINT "fk_equipmen_currency_1bd4eb18";
        DROP INDEX "uid_equipment_charact_56d09e";
        ALTER TABLE "equipment" DROP COLUMN "currency_type_id";
        ALTER TABLE "equipment" DROP COLUMN "price";
        ALTER TABLE "equipment" DROP COLUMN "quantity";"""
