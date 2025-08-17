from faststream.kafka import KafkaRouter 
from core.faststream import get_faststream_router

from .ping import router as ping_router

faststream_router = get_faststream_router() #KafkaRouter()

# Add routers
faststream_router.include_router(ping_router)


# This stay
__all__ = ["faststream_router"]