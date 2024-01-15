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
async def chat_steps(
    request: Request,
    data: _ChatData,
    agent: BaseChatEngine = Depends(get_agent),
):
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )

    def chat_repl(exit_when_done: bool = True):
        """Chat REPL.

        Args:
            exit_when_done(bool): if True, automatically exit when step is finished.
                Set to False if you want to keep going even if step is marked as finished by the agent.
                If False, you need to explicitly call "exit" to finalize a task execution.

        """
        task_message = None
        while task_message != "exit":
            task_message = input(">> Human: ")
            if task_message == "exit":
                break

            task = agent.create_task(task_message)

            response = None
            step_output = None
            message = None
            while message != "exit":
                if message is None or message == "":
                    step_output = agent.run_step(task.task_id)
                else:
                    step_output = agent.run_step(task.task_id, input=message)
                if exit_when_done and step_output.is_last:
                    print(
                        ">> Task marked as finished by the agent, executing task execution."
                    )
                    break

                message = input(
                    ">> Add feedback during step? (press enter/leave blank to continue, and type 'exit' to stop): "
                )
                if message == "exit":
                    break

            if step_output is None:
                print(">> You haven't run the agent. Task is discarded.")
            elif not step_output.is_last:
                print(">> The agent hasn't finished yet. Task is discarded.")
            else:
                response = agent.finalize_response(task.task_id)
            print(f"Agent: {str(response)}")

    chat_repl()

    # response = agent.finalize_response(task.task_id)

    # # stream response
    # async def event_generator():
    #     for token in response.response_gen:
    #         print(token)
    #         # If client closes connection, stop sending events
    #         if await request.is_disconnected():
    #             break
    #         yield token

    # return StreamingResponse(event_generator(), media_type="text/plain")
