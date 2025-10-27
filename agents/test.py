"""
RAG Agent with Memory Manager and Session Summaries
Note: JSON encoder patch must be applied in main.py before importing this module
"""
from uuid import uuid4

from agno.agent.agent import Agent
from agno.memory import MemoryManager
from agno.db.postgres import PostgresDb
from agno.models.lmstudio import LMStudio
from agno.session import SessionSummaryManager

db_url = "postgresql://neondb_owner:npg_hdS5VbDo7gOG@ep-polished-mode-ahhpuyi0-pooler.c-3.us-east-1.aws.neon.tech/genai-project?sslmode=require&channel_binding=require"

db = PostgresDb(db_url=db_url)

# Memory Manager - automatically extracts and stores memories from conversations
memory_manager = MemoryManager(
    db=db,
    model=LMStudio(
        id="qwen3-0.6b",
        base_url="http://localhost:1234/v1",
    ),
    memory_capture_instructions="Extract and store key information about the user including their name, preferences, hobbies, and personal details.",
)

# Setup your Session Summary Manager, to adjust how summaries are created
session_summary_manager = SessionSummaryManager(
    # Select the model used for session summary creation and updates. If not specified, the agent's model is used by default.
    model=LMStudio(
        id="qwen3-0.6b",
        base_url="http://localhost:1234/v1",
    ),
    # You can also overwrite the prompt used for session summary creation
    session_summary_prompt="Create a very succinct summary of the following conversation:",
)

rag_agent = Agent(
    name="RAG Agent",
    model=LMStudio(
        id="qwen3-0.6b",
        base_url="http://localhost:1234/v1",
    ),
    instructions=["You are a helpful assistant. ./no_think"],
    db=db,
    # user_id and session_id are None here - will be provided dynamically by AgentOS per request
    # memory_manager=memory_manager,
    enable_user_memories=True,  # Automatically extracts memories from conversations
    add_history_to_context=True,
    num_history_runs=3,
    session_summary_manager=session_summary_manager,
    enable_session_summaries=True,  # Enabled (requires JSON encoder patch in main.py)
)

rag_agent.print_response(
    "My name is John Doe and I love hiking in the mountains on weekends.",
    stream=True,
)