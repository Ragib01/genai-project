from uuid import uuid4

from agno.agent.agent import Agent
from agno.memory import MemoryManager
from agno.db.postgres import PostgresDb
from agno.models.openai import OpenAIChat
from agno.models.lmstudio import LMStudio
from rich.pretty import pprint

db_url = "postgresql://neondb_owner:npg_hdS5VbDo7gOG@ep-polished-mode-ahhpuyi0-pooler.c-3.us-east-1.aws.neon.tech/genai-project?sslmode=require&channel_binding=require"

db = PostgresDb(db_url=db_url)

# db.clear_memories()

session_id = str(uuid4())
user_id = "john_doe@example.com"

# Cheap model for memory operations (60x less expensive)
memory_manager = MemoryManager(
    db=db,
    model=LMStudio(
        id="qwen3-0.6b",
        base_url="http://localhost:1234/v1",
    ),
    memory_capture_instructions="Capture all the information you can about the user's request. ./no_think",
)

rag_agent = Agent(
    name="RAG Agent",
    model=LMStudio(
        id="qwen/qwen3-1.7b",
        base_url="http://localhost:1234/v1",
    ),
    instructions=["You are a helpful assistant. ./no_think"],
    db=db,
    user_id=user_id,
    session_id=session_id,  # FIXED: Use variable, not string literal
    memory_manager=memory_manager,
    enable_user_memories=True,  # This enables memory storage
    add_history_to_context=True,
    num_history_runs=3,  # Include last 3 runs
    # enable_session_summaries=True,
)
