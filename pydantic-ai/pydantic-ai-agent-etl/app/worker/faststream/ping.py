import logging
from typing import Optional

from faststream.kafka import KafkaRouter
from pydantic import BaseModel, Field

from core.faststream_core import MsgBaseModel, MessageStatus

router = KafkaRouter()


class MessageContent(BaseModel):
    message: str
    timestamp: Optional[str] = None


# Define request/response models
class SampleReqMsg(MsgBaseModel[MessageContent]):
    data: Optional[MessageContent] = None


class SampleResMsg(MsgBaseModel[MessageContent]):
    data: Optional[MessageContent] = None
    status: MessageStatus = Field(default=MessageStatus.RECEIVED)


@router.subscriber("in-topic")
# @router.publisher("out-topic")
async def task_handler(body: SampleReqMsg) -> SampleResMsg:
    logging.info(f"Logging from in-topic when receiving message")

    # Create response
    response = SampleResMsg(
        correlation_id=body.correlation_id,
        data=MessageContent(
            message="pong from subscriber",
            timestamp="2024-03-19T10:00:01Z"
        ),
        status=MessageStatus.COMPLETED
    )
    return response

# @router.subscriber("out-topic")
# async def task_publisher(message: MessageRequest)-> MessageResponse:
#     logging.info(f"Message received via publisher {message.body}")
#     return MessageResponse(message="pong from subscriber")
