from fastapi.routing import APIRouter

from test_task.web.api import (  # noqa: WPS235
    character,
    currency_balance,
    currency_type,
    dummy,
    echo,
    equipment,
    inventory,
    monitoring,
    rabbit,
    redis,
    transaction,
    user,
    user_profile,
)

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(
    user_profile.router,
    prefix="/user_profile",
    tags=["user_profile"],
)
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(
    transaction.router,
    prefix="/transaction",
    tags=["transaction"],
)
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(
    currency_type.router,
    prefix="/currency_type",
    tags=["currency_type"],
)
api_router.include_router(
    currency_balance.router,
    prefix="/currency_balance",
    tags=["currency_balance"],
)
api_router.include_router(character.router, prefix="/character", tags=["character"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(rabbit.router, prefix="/rabbit", tags=["rabbit"])
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
