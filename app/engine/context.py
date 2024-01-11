from llama_index import ServiceContext
import os

from app.engine.constants import CHUNK_SIZE, CHUNK_OVERLAP

from llama_index import ServiceContext
from llama_index.llms import OpenAI

model = os.getenv("MODEL", "gpt-3.5-turbo")

def create_service_context():
    return ServiceContext.from_defaults(
        llm=OpenAI(model=model),
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
