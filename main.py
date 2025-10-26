from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agents.basic_agent import basic_agent
from agents.rag_agent import rag_agent

agent_os = AgentOS(
    id="my-first-os",
    description="My first AgentOS",
    agents=[basic_agent, rag_agent],
)

app = agent_os.get_app()

if __name__ == "__main__":
    # Default port is 7777; change with port=...
    agent_os.serve(app="main:app", reload=False)