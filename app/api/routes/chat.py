from typing import List
import os

from fastapi.responses import StreamingResponse
from llama_index.chat_engine.types import BaseChatEngine
from llama_index.agent.types import BaseAgentWorker

from app.engine.index import get_agent

from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.llms.base import ChatMessage
from llama_index.llms.types import MessageRole
from pydantic import BaseModel


chat_router = r = APIRouter()

# from traceloop.sdk import Traceloop
# traceloop_key = os.getenv("TRACELOOP_API_KEY")

# Traceloop.init(disable_batch=True, api_key=traceloop_key)


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]


@r.post("")
async def chat(
    request: Request,
    data: _ChatData,
    chat_engine: BaseChatEngine = Depends(get_agent),
):
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    print(data)
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    messages = [
        # ChatMessage(
        #     role=m.role,
        #     content=m.content,
        # )
        # for m in data.messages
        ChatMessage(
            role=MessageRole.USER,
            content="Možete li mi reći nešto o fizičkim standardima za pisma?",
        ),
        ChatMessage(
            role=MessageRole.ASSISTANT, 
            content="""
                Fizički standardi za pisma uključuju sljedeće kriterije:

                1. Dimenzije: Pisma moraju biti pravougaona sa četiri ravna ugla i paralelnim suprotnim stranama. Dužina pisma mora biti veća od 5 inča, visina veća od 3-1/2 inča, a debljina veća od 0.007 inča. Pisma ne smiju biti duža od 11-1/2 inča, viša od 6-1/8 inča ili deblja od 1/4 inča.

                2. Težina: Pisma ne smiju biti teža od 3.5 unce.

                3. Nonmachinable karakteristike: Ako pismo ne ispunjava minimalnu debljinu od 0.009 inča, podleže dodatnoj naknadi za nonmachinable karakteristike.

                Nadam se da vam ove informacije pomažu.
            """
        ),
    ]

    response = chat_engine.stream_chat(lastMessage.content, messages)

    # stream response
    async def event_generator():
        for token in response.response_gen:
            print(token)
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
