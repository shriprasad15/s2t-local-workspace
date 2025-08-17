# Just need to replace fastream.[...].fastapi with different StreamRouter if you want to use different stream service.
import logging

from fastapi import Request
from faststream.kafka.fastapi import KafkaRouter

from .config import settings
from .middleware import FaststreamLoggingMiddleware


def get_faststream_router() -> KafkaRouter | None:
    try:
        if settings.FASTSTREAM_PROVIDER is None:
            logging.error(f"FASTSTREAM disabled due to FASTSTREAM_PROVIDER not set")
            return None

        router = KafkaRouter(
            settings.FASTSTREAM_PROVIDER,
            include_in_schema=True,
            middlewares=(FaststreamLoggingMiddleware,),
        )
        return router
    except Exception as e:
        logging.error(f"Failed to connect to Provider in following url {settings.FASTSTREAM_PROVIDER} ")
        return None


async def publish_message(request: Request, message, topic: str):
    try:
        broker = request.state.broker
        if broker:
            await broker.publish(message, topic)
    except Exception as e:
        pass
