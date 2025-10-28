import os
import asyncio
from pathlib import Path

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.chunking.agentic import AgenticChunking
from agno.knowledge.embedder.openai import OpenAIEmbedder

from agno.vectordb.lancedb import LanceDb, SearchType
from agno.vectordb.pgvector import PgVector
from agno.db.sqlite import SqliteDb

from agno.tools.reasoning import ReasoningTools

from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.reader.markdown_reader import MarkdownReader

from dotenv import load_dotenv
load_dotenv()

# Get environment variables
POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY")
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL")
RAG_AGENT_MODEL = os.getenv("RAG_AGENT_MODEL")

# Check if all required environment variables are set
if not POSTGRES_DB_URL:
    raise ValueError("POSTGRES_DB_URL environment variable is required")

if not LM_STUDIO_API_KEY:
    raise ValueError("LM_STUDIO_API_KEY environment variable is required")

if not LM_STUDIO_BASE_URL:
    raise ValueError("LM_STUDIO_BASE_URL environment variable is required")

if not RAG_AGENT_MODEL:
    raise ValueError("RAG_AGENT_MODEL environment variable is required")

from agno.models.lmstudio import LMStudio
from agno.agent.agent import Agent
async def main():
    embedder = OpenAIEmbedder(
        id="text-embedding-nomic-embed-text-v1.5",
        api_key=LM_STUDIO_API_KEY,
        base_url=LM_STUDIO_BASE_URL,
        dimensions=768  # Add this for custom dimensions
    )

    knowledge = Knowledge(
        vector_db=LanceDb(
            table_name="unimart_company_profile",
            uri="tmp/lancedb",
            search_type=SearchType.hybrid, # SearchType.hybrid combines vector (semantic) and keyword (lexical) search for better results. 
            embedder=embedder,
        ),
        max_results=2,
    )

    # PDF Reader
    # await knowledge.add_content_async(
    #     name="orangebd_company_profile",
    #     url="https://www.orangebd.com/pdf/company_profile.pdf",
    #     metadata={"doc_type": "orangebd_company_profile_book"},
    #     reader=PDFReader(
    #         name="Agentic Chunking Reader",
    #         chunking_strategy=AgenticChunking(),
    #     ),
    # )
    
    
    # Markdown Reader
    await knowledge.add_content_async(
        name="unimart company profile",
        path=Path("documents/uiumart_company_profile.md"),
        reader=MarkdownReader(
            name="Markdown Reader",
            chunking_strategy=AgenticChunking(),
        ),
    )
    

    agent = Agent(
        model=LMStudio(
            id=RAG_AGENT_MODEL,
            base_url=LM_STUDIO_BASE_URL,
        ),
        # tools=[ReasoningTools(add_instructions=True, add_few_shot=True, enable_think=True, enable_analyze=True)],
        knowledge=knowledge,
        add_knowledge_to_context=True,
        search_knowledge=True,
        markdown=True,
    )

    await agent.aprint_response("which type of business is unimart?", stream=True, markdown=True)

if __name__ == "__main__":
    asyncio.run(main())
