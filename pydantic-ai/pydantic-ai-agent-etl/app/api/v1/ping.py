import logging

from fastapi import APIRouter, Request

from core.config import settings
from core.faststream import publish_message
from core.saq import get_saq_queue

router = APIRouter()


@router.get("/error")
async def error():
    raise Exception("unhandled error")


@router.get("/ping")
async def ping(request: Request):
    if settings.FASTSTREAM_ENABLE:
        from app.worker.faststream.ping import SampleReqMsg, MessageContent
        ## follow the format of subscriber
        message = SampleReqMsg(
            data=MessageContent(
                message="Send for in-topic",
                timestamp="2024-03-19T10:00:01Z"
            )
        )

        await publish_message(request, message, "in-topic")

    if settings.CELERY_ENABLE:
        from app.worker.celery.tasks import ping as celery_ping
        celery_ping.delay()

    if settings.SAQ_ENABLE:
        logging.info("Attempting to enqueue SAQ ping task")
        queue = get_saq_queue()
        if queue:
            try:
                await queue.enqueue("ping", correlation_id=correlation_id)
                logging.info(f"SAQ ping task enqueued with correlation_id: {correlation_id}")
            except Exception as e:
                logging.error(f"Failed to enqueue SAQ task: {e}")
        else:
            logging.error("SAQ queue not initialized")

    logging.info("Sample logging from ping api")
    logging.debug("Ping request received")
    return {"version": settings.APP_VERSION, "message": "pong"}
