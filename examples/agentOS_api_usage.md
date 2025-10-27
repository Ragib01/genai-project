# Using Dynamic Memories with AgentOS API

## Overview

When using `AgentOS`, the `user_id` and `session_id` are provided **dynamically** through the API request, not hardcoded in the agent definition.

## How It Works

### 1. Agent Definition (rag_agent.py)

```python
rag_agent = Agent(
    name="RAG Agent",
    model=LMStudio(...),
    db=db,
    # user_id and session_id are NOT set here
    # They will be provided by AgentOS per request
    memory_manager=memory_manager,
    enable_user_memories=True,  # Memories extracted automatically
    enable_session_summaries=True,
)
```

### 2. Start AgentOS Server

```bash
python main.py
```

Server will start on http://localhost:7777

### 3. Making API Requests with Dynamic User/Session

#### Example 1: User Alice's First Conversation

```bash
curl -X POST http://localhost:7777/v1/agents/rag-agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi! My name is Alice and I love Python programming.",
    "user_id": "alice@example.com",
    "session_id": "alice-session-001",
    "stream": false
  }'
```

**What happens:**
- User ID: `alice@example.com` (dynamic)
- Session ID: `alice-session-001` (dynamic)
- Memory Manager automatically extracts: "User name is Alice" and "User loves Python programming"
- Memories stored in `agno_memories` table for user `alice@example.com`

#### Example 2: User Alice's Continued Conversation

```bash
curl -X POST http://localhost:7777/v1/agents/rag-agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my interests?",
    "user_id": "alice@example.com",
    "session_id": "alice-session-001",
    "stream": false
  }'
```

**What happens:**
- Same user ID and session ID
- Agent retrieves Alice's stored memories
- Response includes previously stored information about Python programming

#### Example 3: Different User (Bob)

```bash
curl -X POST http://localhost:7777/v1/agents/rag-agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi! I am Bob and I enjoy hiking.",
    "user_id": "bob@example.com",
    "session_id": "bob-session-001",
    "stream": false
  }'
```

**What happens:**
- Different user ID: `bob@example.com` (dynamic)
- Different session ID: `bob-session-001` (dynamic)
- Bob's memories stored separately from Alice's
- Each user has their own isolated memory space

## Memory Topics - Automatic Extraction

When `enable_user_memories=True`, the MemoryManager automatically:

1. **Extracts key facts** from user messages
2. **Categorizes with topics** (e.g., "hobbies", "preferences", "personal")
3. **Stores in database** linked to the specific `user_id`

Example automatic extraction:
- Input: "I love hiking and photography"
- Extracted memories:
  - Memory: "User enjoys hiking" | Topics: ["hobbies", "activities"]
  - Memory: "User likes photography" | Topics: ["hobbies", "interests"]

## Manual Memory Management via API

### Add Memory Manually

```bash
curl -X POST http://localhost:7777/v1/agents/rag-agent/add-memory \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice@example.com",
    "memory": "User prefers dark mode",
    "topics": ["preferences", "ui"]
  }'
```

### Get User Memories

```bash
curl -X GET "http://localhost:7777/v1/agents/rag-agent/memories?user_id=alice@example.com"
```

Response:
```json
[
  {
    "memory_id": "mem-123",
    "memory": "User name is Alice",
    "topics": ["personal", "identity"],
    "user_id": "alice@example.com",
    "created_at": "2025-01-15T10:30:00Z"
  },
  {
    "memory_id": "mem-124",
    "memory": "User loves Python programming",
    "topics": ["skills", "programming", "preferences"],
    "user_id": "alice@example.com",
    "created_at": "2025-01-15T10:31:00Z"
  }
]
```

## Session Summaries - Automatic

Session summaries are also dynamic and created per session:

```bash
curl -X GET "http://localhost:7777/v1/agents/rag-agent/sessions/alice-session-001/summary"
```

Response:
```json
{
  "session_id": "alice-session-001",
  "user_id": "alice@example.com",
  "summary": "User Alice introduced herself and discussed her interest in Python programming. She asked about her interests and the agent recalled her programming preferences.",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z"
}
```

## Database Structure

### agno_memories table
| user_id | memory_id | memory | topics | created_at |
|---------|-----------|---------|---------|------------|
| alice@example.com | mem-123 | User name is Alice | ["personal"] | 2025-01-15 |
| alice@example.com | mem-124 | User loves Python | ["skills"] | 2025-01-15 |
| bob@example.com | mem-125 | User enjoys hiking | ["hobbies"] | 2025-01-15 |

### agno_sessions table
| session_id | user_id | agent_id | summary | created_at |
|-----------|---------|----------|---------|------------|
| alice-session-001 | alice@example.com | rag-agent | User intro... | 2025-01-15 |
| bob-session-001 | bob@example.com | rag-agent | User Bob... | 2025-01-15 |

## Best Practices

1. **Unique user_id**: Use email, UUID, or unique identifier per user
2. **Session per conversation**: New session_id for each distinct conversation thread
3. **Descriptive topics**: Use clear, searchable topic names
4. **Let auto-extraction work first**: Enable `enable_user_memories=True` and let the agent learn
5. **Manual memories for critical info**: Use manual addition for important facts you want guaranteed storage

## Testing Locally

Use the provided examples:

```bash
# Test automatic memory extraction
python agents/rag_agent.py

# Test manual memory management
python examples/dynamic_memories_example.py
```

## Troubleshooting

**Memories not being created?**
1. Check that `enable_user_memories=True` in agent definition
2. Verify `memory_manager` is configured with a model
3. Ensure LM Studio is running and accessible
4. Try a larger model if using a small one (0.6B might be too small)

**Session summaries failing?**
1. Check that JSON encoder patch is applied in `main.py`
2. Verify `enable_session_summaries=True`
3. Check PostgreSQL connection

**Different users seeing each other's memories?**
1. Ensure each user has a unique `user_id` in API requests
2. Check database queries are filtering by `user_id`

