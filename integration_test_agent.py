
from google.adk.agents import LlmAgent
from google.adk.tools.transfer_to_agent_tool import transfer_to_agent

parent_agent = LlmAgent(
    name="parent",
    model="gemini-2.5-pro",
    instruction="You are a parent agent.",
)

child_agent = LlmAgent(
    name="child",
    model="gemini-2.5-pro",
    instruction="You are a child agent.",
    enforce_transfer_to_parent=True,
    tools=[transfer_to_agent],
)

parent_agent.sub_agents = [child_agent]
child_agent.parent_agent = parent_agent

agent = parent_agent
