"""
RAG Agent with Memory Manager and Session Summaries
Note: JSON encoder patch must be applied in main.py before importing this module
"""
from uuid import uuid4
import os
from dotenv import load_dotenv

from agno.agent.agent import Agent
from agno.memory import MemoryManager
from agno.db.postgres import PostgresDb
from agno.models.lmstudio import LMStudio
from agno.session import SessionSummaryManager

from agno.tools.memory import MemoryTools

load_dotenv()

POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY")
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL")
RAG_AGENT_MODEL = os.getenv("RAG_AGENT_MODEL")

db_url = POSTGRES_DB_URL

db = PostgresDb(db_url=db_url)

memory_tools = MemoryTools(
    db=db,
)

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
    tools=[memory_tools],
    instructions=["You are a helpful assistant. ./no_think"],
    db=db,
    # user_id and session_id are None here - will be provided dynamically by AgentOS per request
    # memory_manager=memory_manager,
    # enable_user_memories=True,  # Automatically extracts memories from conversations
    add_history_to_context=True,
    num_history_runs=3,
    session_summary_manager=session_summary_manager,
    enable_session_summaries=True,  # Enabled (requires JSON encoder patch in main.py)
)

# Test the agent when run directly
if __name__ == "__main__":
    # Apply patch for standalone testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.json_encoder import patch_json_encoder
    patch_json_encoder()
    
    # Create dynamic test values
    test_user_id = "john_doe@example.com"
    test_session_id = str(uuid4())
    
    print("\n" + "="*60)
    print("TESTING RAG AGENT WITH MEMORY & SESSION SUMMARIES")
    print("="*60)
    print(f"User ID: {test_user_id}")
    print(f"Session ID: {test_session_id}")
    
    print("\n[Step 1] Providing user information...")
    response1 = rag_agent.run(
        "My name is John Doe and I love hiking in the mountains on weekends.",
        stream=False,
        user_id=test_user_id,
        session_id=test_session_id,
    )
    print(f"Response 1: {response1.content}")
    
    print("\n" + "="*60)
    print("[Step 2] Providing more information...")
    response2 = rag_agent.run(
        "I also enjoy photography and reading science fiction books.",
        stream=False,
        user_id=test_user_id,
        session_id=test_session_id,
    )
    print(f"Response 2: {response2.content}")
    
    print("\n" + "="*60)
    print("[Step 3] Testing memory recall...")
    response3 = rag_agent.run(
        "What are my hobbies?",
        stream=False,
        user_id=test_user_id,
        session_id=test_session_id,
    )
    print(f"Response 3: {response3.content}")
    
    print("\n" + "="*60)
    print("[Step 4] Checking stored memories in database...")
    memories = rag_agent.get_user_memories(user_id=test_user_id)
    print(f"\nMemories found for user '{test_user_id}':")
    if memories:
        pprint(memories)
    else:
        print("⚠️  NO MEMORIES FOUND!")
    
    print("\n" + "="*60)
    print("[Step 5] Checking session summary...")
    session_summary = rag_agent.get_session_summary(session_id=test_session_id)
    if session_summary and session_summary.summary:
        print(f"\nSession Summary:")
        pprint(session_summary.summary)
    else:
        print("⚠️  NO SESSION SUMMARY FOUND!")
    print("="*60 + "\n")