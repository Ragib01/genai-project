"""
Example: Dynamic Memory Management with RAG Agent
Shows how memories work automatically and how to add them manually if needed
"""
from uuid import uuid4
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agno.agent import Agent
from agno.memory import MemoryManager
from agno.db.postgres import PostgresDb
from agno.models.lmstudio import LMStudio
from utils.memory_helpers import add_dynamic_memory, batch_add_memories, search_memories_by_topic
from rich.pretty import pprint

# Database connection
db_url = "postgresql://neondb_owner:npg_hdS5VbDo7gOG@ep-polished-mode-ahhpuyi0-pooler.c-3.us-east-1.aws.neon.tech/genai-project?sslmode=require&channel_binding=require"
db = PostgresDb(db_url=db_url)

# Memory Manager
memory_manager = MemoryManager(
    db=db,
    model=LMStudio(
        id="qwen3-0.6b",
        base_url="http://localhost:1234/v1",
    ),
    memory_capture_instructions="Extract and store key information about the user including their name, preferences, hobbies, and personal details.",
)

# Create agent
agent = Agent(
    name="Dynamic Memory Agent",
    model=LMStudio(
        id="qwen3-0.6b",
        base_url="http://localhost:1234/v1",
    ),
    instructions=["You are a helpful assistant."],
    db=db,
    memory_manager=memory_manager,
    enable_user_memories=True,  # Automatic memory extraction
    add_history_to_context=True,
)

# Example 1: Let agent automatically extract memories from conversation
print("="*70)
print("EXAMPLE 1: Automatic Memory Extraction")
print("="*70)

user_id = "alice@example.com"
session_id = str(uuid4())

print(f"\nUser: {user_id}")
print("Conversation:")

# The agent will automatically extract and store memories from these interactions
response1 = agent.run(
    "Hi! My name is Alice and I'm a data scientist. I love machine learning and Python.",
    user_id=user_id,
    session_id=session_id,
    stream=False,
)
print(f"Agent: {response1.content}")

response2 = agent.run(
    "I also enjoy hiking on weekends and reading sci-fi novels.",
    user_id=user_id,
    session_id=session_id,
    stream=False,
)
print(f"Agent: {response2.content}")

# Check automatically extracted memories
print("\nAutomatically extracted memories:")
memories = agent.get_user_memories(user_id=user_id)
if memories:
    for mem in memories:
        print(f"  - {mem.memory} | Topics: {mem.topics}")
else:
    print("  No memories extracted automatically")

# Example 2: Manually add dynamic memories
print("\n" + "="*70)
print("EXAMPLE 2: Manually Adding Dynamic Memories")
print("="*70)

user_id_2 = "bob@example.com"

# Add single memory
print(f"\nUser: {user_id_2}")
print("Adding individual memories:")

add_dynamic_memory(
    memory_manager=memory_manager,
    user_id=user_id_2,
    memory_text="User prefers dark mode for all applications",
    topics=["preferences", "ui", "settings"]
)
print("  ✓ Added: Dark mode preference")

add_dynamic_memory(
    memory_manager=memory_manager,
    user_id=user_id_2,
    memory_text="User is a software engineer specializing in backend development",
    topics=["career", "professional", "skills"]
)
print("  ✓ Added: Career information")

# Example 3: Batch add memories
print("\n" + "="*70)
print("EXAMPLE 3: Batch Adding Multiple Memories")
print("="*70)

user_id_3 = "charlie@example.com"

memories_to_add = [
    {
        "memory": "User lives in San Francisco, California",
        "topics": ["personal", "location", "geography"]
    },
    {
        "memory": "User is allergic to peanuts",
        "topics": ["health", "allergies", "diet"]
    },
    {
        "memory": "User speaks English, Spanish, and French",
        "topics": ["languages", "skills", "communication"]
    },
    {
        "memory": "User's favorite programming language is Python",
        "topics": ["programming", "preferences", "technology"]
    },
]

print(f"\nUser: {user_id_3}")
print("Adding batch memories:")

batch_add_memories(
    memory_manager=memory_manager,
    user_id=user_id_3,
    memories=memories_to_add
)
print(f"  ✓ Added {len(memories_to_add)} memories in batch")

# Verify batch memories
all_memories = memory_manager.get_user_memories(user_id=user_id_3)
print(f"\nTotal memories for {user_id_3}: {len(all_memories) if all_memories else 0}")
if all_memories:
    for mem in all_memories:
        print(f"  - {mem.memory}")

# Example 4: Search memories by topic
print("\n" + "="*70)
print("EXAMPLE 4: Search Memories by Topic")
print("="*70)

programming_memories = search_memories_by_topic(
    memory_manager=memory_manager,
    user_id=user_id_3,
    topic="programming"
)

print(f"\nMemories with topic 'programming' for {user_id_3}:")
if programming_memories:
    for mem in programming_memories:
        print(f"  - {mem.memory} | Topics: {mem.topics}")
else:
    print("  No memories found")

# Example 5: Using memories in conversation
print("\n" + "="*70)
print("EXAMPLE 5: Agent Using Stored Memories")
print("="*70)

print(f"\nAsking agent about {user_id_3}:")
response = agent.run(
    "What do you know about me?",
    user_id=user_id_3,
    session_id=str(uuid4()),
    stream=False,
)
print(f"Agent: {response.content}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("\n✓ Automatic memory extraction from conversations")
print("✓ Manual memory addition with dynamic content")
print("✓ Batch memory operations")
print("✓ Memory search by topics")
print("✓ Agent retrieval and use of memories in conversations")
print("\n" + "="*70)

