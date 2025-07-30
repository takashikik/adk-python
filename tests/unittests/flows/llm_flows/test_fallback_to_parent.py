from __future__ import annotations

import pytest
from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.flows.llm_flows.base_llm_flow import BaseLlmFlow
from google.adk.tools.transfer_to_agent_tool import transfer_to_agent
from tests.unittests.testing_utils import create_invocation_context
from tests.unittests.testing_utils import MockModel


@pytest.mark.asyncio
async def test_enforce_transfer_to_parent_transfers_control():
    """Tests that the agent transfers control to the parent when enforce_transfer_to_parent is True."""
    parent_agent = LlmAgent(
        name="parent",
        model=MockModel.create(responses=["Response from parent"]),
    )
    child_agent = LlmAgent(
        name="child",
        model=MockModel.create(responses=["Response from child"]),
        fallback_to_parent=True,
        tools=[transfer_to_agent],
    )
    parent_agent.sub_agents = [child_agent]
    child_agent.parent_agent = parent_agent

    invocation_context = await create_invocation_context(child_agent, "hello")
    flow = BaseLlmFlow()
    events = []
    async for event in flow._run_one_step_async(invocation_context):
        events.append(event)

    assert len(events) == 3
    assert events[0].author == "child"
    assert events[0].get_function_calls()[0].name == "transfer_to_agent"
    assert events[0].get_function_calls()[0].args["agent_name"] == "parent"
    assert events[1].author == "child"
    assert events[2].author == "parent"
    assert "Response from parent" in events[2].content.parts[0].text


@pytest.mark.asyncio
async def test_enforce_transfer_to_parent_and_disallow_raises_error():
    """Tests that ValueError is raised when enforce_transfer_to_parent and disallow_transfer_to_parent are both True."""
    with pytest.raises(ValueError):
        LlmAgent(
            name="test_agent",
            model="gemini-2.5-pro",
            fallback_to_parent=True,
            disallow_transfer_to_parent=True,
        )


@pytest.mark.asyncio
async def test_enforce_transfer_to_parent_with_output_schema_raises_error():
    """Tests that ValueError is raised when fallback_to_parent is True and output_schema is set."""
    from pydantic import BaseModel

    class MySchema(BaseModel):
        message: str

    with pytest.raises(ValueError):
        LlmAgent(
            name="test_agent",
            model="gemini-2.5-pro",
            fallback_to_parent=True,
            output_schema=MySchema,
        )
