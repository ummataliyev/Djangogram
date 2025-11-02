from .start import router as start_router
from .booking import router as booking_router
from .stop import router as stop_router
from .notify import router as notify_router

all_routers = [
    start_router,
    booking_router,
    stop_router,
    notify_router,
]


def register_all(dp):
    """
    Registers all routers in the dispatcher.

    This function iterates through all defined routers in the `all_routers` list
    and includes them into the provided dispatcher instance. It helps organize
    and modularize bot command/event handlers.

    :param dp: Dispatcher instance (usually from aiogram) to which all routers will be attached.
    :type dp: aiogram.Dispatcher
    :return: None
    """
    for router in all_routers:
        dp.include_router(router)
