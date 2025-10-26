"""
Simple script to test memory storage with Agno
Run this to verify your memory configuration is working
"""
from uuid import uuid4
from agno.agent import Agent
from agno.memory import MemoryManager
from agno.db.postgres import PostgresDb
from agno.models.lmstudio import LMStudio
from rich.pretty import pprint

# Database connection
db_url = "postgresql://neondb_owner:npg_hdS5VbDo7gOG@ep-polished-mode-ahhpuyi0-pooler.c-3.us-east-1.aws.neon.tech/genai-project?sslmode=require&channel_binding=require"
db = PostgresDb(db_url=db_url)

# User info
user_id = "test_user@example.com"
session_id = str(uuid4())

print(f"User ID: {user_id}")
print(f"Session ID: {session_id}")

# Memory Manager
memory_manager = MemoryManager(
    db=db,
    model=LMStudio(
        id="qwen/qwen3-1.7b",
        base_url="http://localhost:1234/v1",
    ),
    memory_capture_instructions="Capture important information about the user",
)

# Create agent with memory
agent = Agent(
    name="Memory Test Agent",
    model=LMStudio(
        id="qwen/qwen3-1.7b",
        base_url="http://localhost:1234/v1",
    ),
    instructions=["You are a helpful assistant."],
    db=db,
    user_id=user_id,
    session_id=session_id,
    memory_manager=memory_manager,
    enable_user_memories=True,  # This is all you need!
    add_history_to_context=True,
)

print("\n" + "="*70)
print("STEP 1: Storing Information")
print("="*70)
agent.print_response(
    "My name is Alice and I love playing tennis. I work as a software engineer.",
    stream=True,
)

print("\n" + "="*70)
print("STEP 2: Recalling Information")
print("="*70)
agent.print_response(
    "What do you know about me?",
    stream=True,
)

print("\n" + "="*70)
print("STEP 3: Database Check")
print("="*70)
memories = agent.get_user_memories(user_id=user_id)
print(f"\nTotal memories stored: {len(memories) if memories else 0}")
if memories:
    print("\nMemory details:")
    pprint(memories)
else:
    print("❌ NO MEMORIES STORED!")
    print("\nTroubleshooting:")
    print("1. Check if LM Studio is running on http://localhost:1234")
    print("2. Verify the model 'qwen/qwen3-1.7b' is loaded")
    print("3. Check PostgreSQL connection")
    print("4. Ensure enable_user_memories=True and memory_manager is configured")

print("="*70)

