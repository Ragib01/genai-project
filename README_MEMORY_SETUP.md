# Dynamic Memory & Session Management - Complete Guide

This guide explains how to use **dynamic memories** and **session summaries** with your RAG Agent in Agno.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [How It Works](#how-it-works)
3. [Automatic Memory Extraction](#automatic-memory-extraction)
4. [Manual Memory Management](#manual-memory-management)
5. [Testing](#testing)
6. [API Usage](#api-usage)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### 1. Start the AgentOS Server

```bash
python main.py
```

Server runs on `http://localhost:7777`

### 2. Make API Request with Dynamic User

```bash
curl -X POST http://localhost:7777/v1/agents/rag-agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi! My name is Alice and I love Python programming.",
    "user_id": "alice@example.com",
    "session_id": "session-123",
    "stream": false
  }'
```

✅ **That's it!** Memories are automatically extracted and stored for `alice@example.com`.

---

## 🔧 How It Works

### Agent Definition (Dynamic - No Hardcoded Values)

```python
# agents/rag_agent.py
rag_agent = Agent(
    name="RAG Agent",
    model=LMStudio(id="qwen3-0.6b", base_url="http://localhost:1234/v1"),
    db=db,
    # ❌ NO user_id or session_id here
    # ✅ They come from API requests dynamically
    memory_manager=memory_manager,
    enable_user_memories=True,  # Auto-extract memories
    enable_session_summaries=True,  # Auto-create summaries
)
```

### Per-Request Values (Dynamic)

When you call the agent via API:
- `user_id` → Identifies the user (e.g., "alice@example.com")
- `session_id` → Identifies the conversation thread (e.g., "session-123")
- `message` → The user's message

Each user gets **their own isolated memories**.

---

## 🤖 Automatic Memory Extraction

When `enable_user_memories=True`, the agent automatically:

1. **Analyzes** user messages
2. **Extracts** key facts
3. **Categorizes** with topics
4. **Stores** in PostgreSQL

### Example

**User Input:**
```
"Hi! My name is Alice. I love hiking and photography. I work as a data scientist."
```

**Automatically Extracted Memories:**
| Memory | Topics |
|--------|--------|
| User name is Alice | `["personal", "identity"]` |
| User enjoys hiking | `["hobbies", "activities"]` |
| User likes photography | `["hobbies", "interests"]` |
| User works as data scientist | `["career", "professional"]` |

### Memory Retrieval

On subsequent messages from the same user:

**User Input:**
```
"What are my hobbies?"
```

**Agent Response:**
```
"Based on our previous conversation, you enjoy hiking and photography!"
```

---

## 📝 Manual Memory Management

If automatic extraction isn't working or you need precise control, use manual methods.

### Helper Functions

Located in `utils/memory_helpers.py`:

#### 1. Add Single Memory

```python
from utils.memory_helpers import add_dynamic_memory

add_dynamic_memory(
    memory_manager=memory_manager,
    user_id="alice@example.com",
    memory_text="User prefers dark mode",
    topics=["preferences", "ui"]
)
```

#### 2. Batch Add Memories

```python
from utils.memory_helpers import batch_add_memories

memories = [
    {"memory": "User lives in San Francisco", "topics": ["location", "personal"]},
    {"memory": "User speaks English and Spanish", "topics": ["languages", "skills"]},
    {"memory": "User is allergic to peanuts", "topics": ["health", "allergies"]},
]

batch_add_memories(
    memory_manager=memory_manager,
    user_id="alice@example.com",
    memories=memories
)
```

#### 3. Search by Topic

```python
from utils.memory_helpers import search_memories_by_topic

programming_memories = search_memories_by_topic(
    memory_manager=memory_manager,
    user_id="alice@example.com",
    topic="programming"
)
```

---

## 🧪 Testing

### Test 1: Automatic Memory Extraction

```bash
python agents/rag_agent.py
```

**Output:**
- Creates test user and session
- Sends multiple messages
- Checks if memories were stored
- Shows session summary

### Test 2: Manual Memory Management

```bash
python examples/dynamic_memories_example.py
```

**Demonstrates:**
- Automatic extraction
- Manual single memory addition
- Batch memory addition
- Topic-based search
- Memory retrieval in conversations

### Test 3: Memory Storage

```bash
python test_memory.py
```

**With debug logging** to see detailed memory creation process.

---

## 🌐 API Usage

### Create Conversation (Alice)

```bash
curl -X POST http://localhost:7777/v1/agents/rag-agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I love Python and machine learning!",
    "user_id": "alice@example.com",
    "session_id": "alice-session-1"
  }'
```

### Create Conversation (Bob - Different User)

```bash
curl -X POST http://localhost:7777/v1/agents/rag-agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I enjoy hiking and photography!",
    "user_id": "bob@example.com",
    "session_id": "bob-session-1"
  }'
```

### Retrieve Alice's Memories

```bash
curl -X GET "http://localhost:7777/v1/agents/rag-agent/memories?user_id=alice@example.com"
```

### Retrieve Bob's Memories

```bash
curl -X GET "http://localhost:7777/v1/agents/rag-agent/memories?user_id=bob@example.com"
```

**Result:** Alice and Bob have **completely separate memories**.

---

## 🔍 Troubleshooting

### ❌ No Memories Being Stored

**Possible Causes:**
1. Model too small (`qwen3-0.6b` might not extract memories well)
2. LM Studio not running
3. Database connection issue

**Solutions:**
```python
# Try a larger model for memory extraction
memory_manager = MemoryManager(
    db=db,
    model=LMStudio(
        id="qwen3-4b-customer-support:2",  # Larger model
        base_url="http://localhost:1234/v1",
    ),
    memory_capture_instructions="Extract key facts..."
)
```

### ❌ Session Summary DateTime Error

**Cause:** JSON serialization issue with PostgreSQL

**Solution:** Already fixed in `main.py`:
```python
# JSON encoder patch applied BEFORE imports
from utils.json_encoder import patch_json_encoder
patch_json_encoder()
```

### ❌ Different Users Seeing Each Other's Memories

**Cause:** Not providing unique `user_id` per request

**Solution:** Always include unique `user_id` in API calls:
```json
{
  "message": "...",
  "user_id": "unique-user-id-here",  // ✅ Different for each user
  "session_id": "session-id-here"
}
```

### ❌ LM Studio Connection Error

**Cause:** LM Studio not running or wrong port

**Solutions:**
1. Start LM Studio
2. Load a model (e.g., `qwen3-0.6b`)
3. Start local server (default port `1234`)
4. Verify: `curl http://localhost:1234/v1/models`

---

## 📊 Database Schema

### agno_memories

```sql
SELECT * FROM agno_memories;
```

| Column | Type | Description |
|--------|------|-------------|
| memory_id | UUID | Unique memory ID |
| user_id | VARCHAR | User identifier |
| memory | TEXT | Memory content |
| topics | JSON | Array of topics |
| agent_id | VARCHAR | Agent that created it |
| created_at | TIMESTAMP | Creation time |

### agno_sessions

```sql
SELECT * FROM agno_sessions;
```

| Column | Type | Description |
|--------|------|-------------|
| session_id | UUID | Unique session ID |
| user_id | VARCHAR | User identifier |
| agent_id | VARCHAR | Agent identifier |
| summary | JSON | Session summary |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

---

## 📚 Files Overview

| File | Purpose |
|------|---------|
| `agents/rag_agent.py` | RAG Agent definition (no hardcoded values) |
| `main.py` | AgentOS server (applies JSON patch) |
| `utils/memory_helpers.py` | Helper functions for manual memory management |
| `utils/json_encoder.py` | Fix for datetime serialization |
| `examples/dynamic_memories_example.py` | Complete memory management examples |
| `examples/agentOS_api_usage.md` | API usage documentation |
| `test_memory.py` | Debug test with logging |

---

## ✅ Best Practices

1. **Unique User IDs**: Use email, UUID, or unique identifier per user
2. **Session Per Conversation**: Create new session_id for each conversation thread
3. **Descriptive Topics**: Use clear topic names for easy searching
4. **Auto-Extract First**: Let the agent try automatic extraction before manual
5. **Larger Models for Memory**: Use at least 1.7B+ model for reliable memory extraction
6. **Test Locally**: Use provided test scripts before deploying

---

## 🎯 Quick Reference

### Enable Memories
```python
Agent(
    enable_user_memories=True,  # ✅ Auto-extract
    memory_manager=memory_manager,
)
```

### Enable Session Summaries
```python
Agent(
    enable_session_summaries=True,  # ✅ Auto-summarize
    session_summary_manager=session_summary_manager,
)
```

### Dynamic API Call
```python
agent.run(
    message="Hello!",
    user_id="user-123",      # ✅ Dynamic per user
    session_id="session-abc" # ✅ Dynamic per session
)
```

---

## 🤝 Need Help?

- Check logs: Enable debug mode with `debug_mode=True` in Agent
- Test locally: Run `python agents/rag_agent.py`
- View examples: See `examples/` directory
- Check database: Query `agno_memories` and `agno_sessions` tables

---

**🎉 You're all set! Your RAG agent now has dynamic, per-user memory management!**

