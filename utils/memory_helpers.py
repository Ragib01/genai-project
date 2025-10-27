"""
Helper functions for dynamic memory management
Use these when you need to manually add, update, or manage memories
"""
from typing import List, Optional
from agno.memory import MemoryManager, UserMemory
from uuid import uuid4


def add_dynamic_memory(
    memory_manager: MemoryManager,
    user_id: str,
    memory_text: str,
    topics: Optional[List[str]] = None,
    agent_id: Optional[str] = None,
) -> UserMemory:
    """
    Dynamically add a memory for a user
    
    Args:
        memory_manager: The MemoryManager instance
        user_id: The user's ID
        memory_text: The memory content (e.g., "User prefers dark mode")
        topics: List of topics/tags (e.g., ["preferences", "ui"])
        agent_id: Optional agent ID that created this memory
    
    Returns:
        UserMemory: The created memory object
    
    Example:
        add_dynamic_memory(
            memory_manager=memory_manager,
            user_id="user123",
            memory_text="User loves Python programming",
            topics=["preferences", "programming", "skills"]
        )
    """
    memory = UserMemory(
        memory_id=str(uuid4()),
        memory=memory_text,
        topics=topics or [],
        agent_id=agent_id,
        user_id=user_id,
    )
    
    result = memory_manager.add_user_memory(
        memory=memory,
        user_id=user_id
    )
    
    return result


def extract_memories_from_conversation(
    memory_manager: MemoryManager,
    user_id: str,
    conversation_text: str,
    agent_id: Optional[str] = None,
) -> str:
    """
    Manually trigger memory extraction from a conversation
    
    Args:
        memory_manager: The MemoryManager instance
        user_id: The user's ID
        conversation_text: The conversation text to extract memories from
        agent_id: Optional agent ID
    
    Returns:
        str: Response from the memory creation process
    
    Example:
        extract_memories_from_conversation(
            memory_manager=memory_manager,
            user_id="user123",
            conversation_text="I love hiking and photography. I work as a software engineer."
        )
    """
    response = memory_manager.create_user_memories(
        message=conversation_text,
        user_id=user_id,
        agent_id=agent_id,
    )
    
    return response


def batch_add_memories(
    memory_manager: MemoryManager,
    user_id: str,
    memories: List[dict],
) -> List[UserMemory]:
    """
    Add multiple memories at once
    
    Args:
        memory_manager: The MemoryManager instance
        user_id: The user's ID
        memories: List of memory dicts with 'memory' and 'topics' keys
    
    Returns:
        List[UserMemory]: List of created memory objects
    
    Example:
        batch_add_memories(
            memory_manager=memory_manager,
            user_id="user123",
            memories=[
                {"memory": "User loves Python", "topics": ["programming", "preferences"]},
                {"memory": "User lives in New York", "topics": ["personal", "location"]},
                {"memory": "User is a software engineer", "topics": ["career", "professional"]},
            ]
        )
    """
    results = []
    
    for mem_data in memories:
        memory = UserMemory(
            memory_id=str(uuid4()),
            memory=mem_data.get("memory", ""),
            topics=mem_data.get("topics", []),
            user_id=user_id,
        )
        
        result = memory_manager.add_user_memory(
            memory=memory,
            user_id=user_id
        )
        
        if result:
            results.append(result)
    
    return results


def update_memory_topics(
    memory_manager: MemoryManager,
    user_id: str,
    memory_id: str,
    new_topics: List[str],
) -> Optional[UserMemory]:
    """
    Update the topics for an existing memory
    
    Args:
        memory_manager: The MemoryManager instance
        user_id: The user's ID
        memory_id: The ID of the memory to update
        new_topics: New list of topics
    
    Returns:
        UserMemory: Updated memory object or None
    """
    return memory_manager.update_memory(
        memory_id=memory_id,
        topics=new_topics,
        user_id=user_id,
    )


def search_memories_by_topic(
    memory_manager: MemoryManager,
    user_id: str,
    topic: str,
) -> List[UserMemory]:
    """
    Search user memories by a specific topic
    
    Args:
        memory_manager: The MemoryManager instance
        user_id: The user's ID
        topic: The topic to search for
    
    Returns:
        List[UserMemory]: List of memories matching the topic
    """
    all_memories = memory_manager.get_user_memories(user_id=user_id)
    
    if not all_memories:
        return []
    
    # Filter memories by topic
    matching_memories = [
        mem for mem in all_memories
        if topic.lower() in [t.lower() for t in (mem.topics or [])]
    ]
    
    return matching_memories

