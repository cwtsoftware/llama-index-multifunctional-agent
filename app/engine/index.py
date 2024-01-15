import logging
import os
from llama_index import (
    StorageContext,
    load_index_from_storage,
)
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.agent import OpenAIAgent

from llama_index.tools import FunctionTool

from app.engine.tools.multiply import MultiplySpec
from app.engine.tools.calendar import CalendarSpec
from app.engine.tools.add import add


from app.engine.constants import STORAGE_DIR
from app.engine.context import create_service_context


def get_agent():
    service_context = create_service_context()
    # check if storage already exists
    if not os.path.exists(STORAGE_DIR):
        raise Exception(
            "StorageContext is empty - call 'python app/engine/generate.py' to generate the storage first"
        )
    logger = logging.getLogger("uvicorn")
    # load the existing index
    logger.info(f"Loading index from {STORAGE_DIR}...")
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)

    index = load_index_from_storage(storage_context, service_context=service_context)
    logger.info(f"Finished loading index from {STORAGE_DIR}")

    query_engine = index.as_query_engine(streaming=True, similarity_top_k=3)

    query_engine_tools = [
        QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name="Physical_Standards_for_Letters_Cards_Flats_and_Parcels",
                description=(
                    "Provides information about Physical Standards for Letters, Cards, Flats, and Parcels. "
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        )
    ]

    multiply_tool = MultiplySpec().to_tool_list()
    add_tool = FunctionTool.from_defaults(fn=add)
    calendar_tool = CalendarSpec().to_tool_list()

    tools = calendar_tool + multiply_tool + query_engine_tools + [add_tool]

    agent = OpenAIAgent.from_tools(
        tools, 
        verbose=True,
        system_prompt="""
            - you are a Croatian assistant working only on Croatian language
            - The questions are for Physical Standards
            - Remember to always use available tools if they are needed
            - always respond in Croatian language, do not confuse it with Serbian or Bosnian or Slovenian
            - check if the respond is in correct Croatian language
        """,
    )



    return agent


