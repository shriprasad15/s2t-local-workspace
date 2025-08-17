import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

router = APIRouter()

_MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # 15 seconds


def _data_generator(max_second: int, period: int):
    counter = 0
    start_time = time.time()
    while time.time() - start_time < max_second:
        yield {"elapsed_seconds": f"{int(time.time() - start_time)}s"}

        counter += 1
        time.sleep(period)


async def _wrapped_sse_responder(max_second: int, period: int):
    counter = 0
    for d in _data_generator(max_second, period):
        yield ServerSentEvent(
            id=f"{counter}",
            retry=_MESSAGE_STREAM_RETRY_TIMEOUT,
            data=d,
            event="data"
        )
        counter += 1
    yield ServerSentEvent(
        id=f"{counter}",
        retry=_MESSAGE_STREAM_RETRY_TIMEOUT,
        event="eol"
    )


async def _inline_sse_responder(max_second: int, period: int):
    counter = 0
    for d in _data_generator(max_second, period):
        yield f"data: {d}\n\n"

        counter += 1


@router.get("/sse")
async def sse(max_second: int = 5, period: int = 1):
    return EventSourceResponse(_wrapped_sse_responder(max_second, period))


@router.get("/inline-sse")
async def inline_sse(max_second: int = 5, period: int = 1):
    return StreamingResponse(_inline_sse_responder(max_second, period), media_type='text/event-stream')
