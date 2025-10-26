from agno.agent import Agent
from agno.models.lmstudio import LMStudio

basic_agent = Agent(
    name="Base model",
    model=LMStudio(
        id="qwen/qwen3-1.7b",
        base_url="http://localhost:1234/v1",
    ),
    instructions=["You are a helpful assistant. ./no_think"],
    reasoning=False,
    markdown=True
)

# Print the response in the terminal
# basic_agent.print_response("Share a 2 sentence horror story.", stream=True)