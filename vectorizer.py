import os
import asyncio

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.chunking.agentic import AgenticChunking
from agno.knowledge.embedder.openai import OpenAIEmbedder

from agno.vectordb.lancedb import LanceDb, SearchType
from agno.vectordb.pgvector import PgVector
from agno.db.sqlite import SqliteDb

from agno.knowledge.reader.pdf_reader import PDFReader

from dotenv import load_dotenv
load_dotenv()

POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY")
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL")
RAG_AGENT_MODEL = os.getenv("RAG_AGENT_MODEL")

embedder = OpenAIEmbedder(
    id="text-embedding-nomic-embed-text-v1.5",
    api_key=LM_STUDIO_API_KEY,
    base_url=LM_STUDIO_BASE_URL,
    dimensions=768  # Add this for custom dimensions
)

# vector_db = LanceDb(
#     table_name="orangebd_company_profile",
#     uri="tmp/lancedb",
#     search_type=SearchType.vector, # SearchType.hybrid combines vector (semantic) and keyword (lexical) search for better results. 
#     embedder=embedder
# )

# knowledge = Knowledge(
#     name="Basic SDK Knowledge Base",
#     description="Agno 2.0 Knowledge Implementation with LanceDB",
#     vector_db=vector_db,
#     contents_db=contents_db,
# )

# if __name__ == "__main__":
#     print("Adding content to the knowledge base...")    
#     asyncio.run(
#         knowledge.add_content_async(
#             name="Orangebd Company Profile",
#             url="https://www.orangebd.com/pdf/company_profile.pdf",
#             metadata={"doc_type": "orangebd_company_profile_book"},
#             reader=PDFReader(
#                 name="Agentic Chunking Reader",
#                 chunking_strategy=AgenticChunking(),
#             ),
#         )
#     )

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
            table_name="orangebd_company_profile",
            uri="tmp/lancedb",
            search_type=SearchType.hybrid,
            embedder=embedder,
        ),
        max_results=2,
    )

    # Use await properly inside async function
    await knowledge.add_content_async(
        name="orangebd_company_profile",
        url="https://www.orangebd.com/pdf/company_profile.pdf",
        metadata={"doc_type": "orangebd_company_profile_book"},
        reader=PDFReader(
            name="Agentic Chunking Reader",
            chunking_strategy=AgenticChunking(),
        ),
    )
    

    agent = Agent(
        model=LMStudio(
            id=RAG_AGENT_MODEL,
            base_url=LM_STUDIO_BASE_URL,
        ),
        knowledge=knowledge,
        add_knowledge_to_context=True,
        search_knowledge=True,
        markdown=True,
    )

    await agent.aprint_response("tell me about orangedb DigitalBangsamoro Portal ./no_think", stream=True, markdown=True)

if __name__ == "__main__":
    asyncio.run(main())
