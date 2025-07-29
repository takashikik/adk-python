# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for canonical_xxx fields in LlmAgent."""

from typing import Any
from typing import cast
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.events.event import Event
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.registry import LLMRegistry
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from pydantic import BaseModel
import pytest
import pytest_mock

from .. import testing_utils


def test_canonical_model_empty():
  agent = LlmAgent(name="test_agent")

  with pytest.raises(ValueError):
    _ = agent.canonical_model


def test_canonical_model_str():
  agent = LlmAgent(name="test_agent", model="gemini-pro")

  assert agent.canonical_model.model == "gemini-pro"


def test_canonical_model_llm():
  llm = LLMRegistry.new_llm("gemini-pro")
  agent = LlmAgent(name="test_agent", model=llm)

  assert agent.canonical_model == llm


def test_canonical_model_inherit():
  sub_agent = LlmAgent(name="sub_agent")
  parent_agent = LlmAgent(
      name="parent_agent", model="gemini-pro", sub_agents=[sub_agent]
  )

  assert sub_agent.canonical_model == parent_agent.canonical_model


async def test_canonical_instruction_str():
  agent = LlmAgent(name="test_agent", instruction="instruction")
  ctx = await testing_utils.create_parent_invocation_context(
      "test_canonical_instruction_str", agent
  )

  canonical_instruction, bypass_state_injection = (
      await agent.canonical_instruction(ReadonlyContext(ctx))
  )
  assert canonical_instruction == "instruction"
  assert not bypass_state_injection


async def test_canonical_instruction():
  def _instruction_provider(ctx: ReadonlyContext) -> str:
    return f'instruction: {ctx.state["state_var"]}'

  agent = LlmAgent(name="test_agent", instruction=_instruction_provider)
  ctx = await testing_utils.create_parent_invocation_context(
      "test_canonical_instruction", agent, state={"state_var": "state_value"}
  )

  canonical_instruction, bypass_state_injection = (
      await agent.canonical_instruction(ReadonlyContext(ctx))
  )
  assert canonical_instruction == "instruction: state_value"
  assert bypass_state_injection


async def test_async_canonical_instruction():
  async def _instruction_provider(ctx: ReadonlyContext) -> str:
    return f'instruction: {ctx.state["state_var"]}'

  agent = LlmAgent(name="test_agent", instruction=_instruction_provider)
  ctx = await testing_utils.create_parent_invocation_context(
      "test_async_canonical_instruction",
      agent,
      state={"state_var": "state_value"},
  )

  canonical_instruction, bypass_state_injection = (
      await agent.canonical_instruction(ReadonlyContext(ctx))
  )
  assert canonical_instruction == "instruction: state_value"
  assert bypass_state_injection


async def test_canonical_global_instruction_str():
  agent = LlmAgent(name="test_agent", global_instruction="global instruction")
  ctx = await testing_utils.create_parent_invocation_context(
      "test_canonical_global_instruction_str", agent
  )

  canonical_instruction, bypass_state_injection = (
      await agent.canonical_global_instruction(ReadonlyContext(ctx))
  )
  assert canonical_instruction == "global instruction"
  assert not bypass_state_injection


async def test_canonical_global_instruction():
  def _global_instruction_provider(ctx: ReadonlyContext) -> str:
    return f'global instruction: {ctx.state["state_var"]}'

  agent = LlmAgent(
      name="test_agent", global_instruction=_global_instruction_provider
  )
  ctx = await testing_utils.create_parent_invocation_context(
      "test_canonical_global_instruction",
      agent,
      state={"state_var": "state_value"},
  )

  canonical_global_instruction, bypass_state_injection = (
      await agent.canonical_global_instruction(ReadonlyContext(ctx))
  )
  assert canonical_global_instruction == "global instruction: state_value"
  assert bypass_state_injection


async def test_async_canonical_global_instruction():
  async def _global_instruction_provider(ctx: ReadonlyContext) -> str:
    return f'global instruction: {ctx.state["state_var"]}'

  agent = LlmAgent(
      name="test_agent", global_instruction=_global_instruction_provider
  )
  ctx = await testing_utils.create_parent_invocation_context(
      "test_async_canonical_global_instruction",
      agent,
      state={"state_var": "state_value"},
  )
  canonical_global_instruction, bypass_state_injection = (
      await agent.canonical_global_instruction(ReadonlyContext(ctx))
  )
  assert canonical_global_instruction == "global instruction: state_value"
  assert bypass_state_injection


def test_output_schema_will_disable_transfer(caplog: pytest.LogCaptureFixture):
  with caplog.at_level("WARNING"):

    class Schema(BaseModel):
      pass

    agent = LlmAgent(
        name="test_agent",
        output_schema=Schema,
    )

    # Transfer is automatically disabled
    assert agent.disallow_transfer_to_parent
    assert agent.disallow_transfer_to_peers
    assert (
        "output_schema cannot co-exist with agent transfer configurations."
        in caplog.text
    )


def test_output_schema_with_sub_agents_will_throw():
  class Schema(BaseModel):
    pass

  sub_agent = LlmAgent(
      name="sub_agent",
  )

  with pytest.raises(ValueError):
    _ = LlmAgent(
        name="test_agent",
        output_schema=Schema,
        sub_agents=[sub_agent],
    )


def test_output_schema_with_tools_will_throw():
  class Schema(BaseModel):
    pass

  def _a_tool():
    pass

  with pytest.raises(ValueError):
    _ = LlmAgent(
        name="test_agent",
        output_schema=Schema,
        tools=[_a_tool],
    )


def test_before_model_callback():
  def _before_model_callback(
      callback_context: CallbackContext,
      llm_request: LlmRequest,
  ) -> None:
    return None

  agent = LlmAgent(
      name="test_agent", before_model_callback=_before_model_callback
  )

  # TODO: add more logic assertions later.
  assert agent.before_model_callback is not None


def test_validate_generate_content_config_thinking_config_throw():
  with pytest.raises(ValueError):
    _ = LlmAgent(
        name="test_agent",
        generate_content_config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig()
        ),
    )


def test_validate_generate_content_config_tools_throw():
  with pytest.raises(ValueError):
    _ = LlmAgent(
        name="test_agent",
        generate_content_config=types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=[])]
        ),
    )


def test_validate_generate_content_config_system_instruction_throw():
  with pytest.raises(ValueError):
    _ = LlmAgent(
        name="test_agent",
        generate_content_config=types.GenerateContentConfig(
            system_instruction="system instruction"
        ),
    )


def test_validate_generate_content_config_response_schema_throw():
  class Schema(BaseModel):
    pass

  with pytest.raises(ValueError):
    _ = LlmAgent(
        name="test_agent",
        generate_content_config=types.GenerateContentConfig(
            response_schema=Schema
        ),
    )



from google.adk.tools.transfer_to_agent_tool import transfer_to_agent


@pytest.mark.asyncio
async def test_enforce_transfer_to_parent(
    mocker: pytest_mock.MockerFixture, request: pytest.FixtureRequest
):
  async def mock_run_async_impl(self, ctx):
    yield Event(
        author=self.name,
        branch=ctx.branch,
        invocation_id=ctx.invocation_id,
        content=types.Content(
            parts=[
                types.Part(
                    function_call=types.FunctionCall(
                        name=transfer_to_agent.__name__,
                        args={"agent_name": f"{request.function.__name__}_parent"},
                    )
                )
            ]
        ),
    )

  mocker.patch(
      "google.adk.agents.llm_agent.LlmAgent._run_async_impl",
      mock_run_async_impl,
  )

  sub_agent = LlmAgent(
      name=f"{request.function.__name__}_sub_agent",
      enforce_transfer_to_parent=True,
      model="gemini-pro",
  )
  parent = LlmAgent(
      name=f"{request.function.__name__}_parent",
      sub_agents=[sub_agent],
      model="gemini-pro",
  )
  parent_ctx = await testing_utils.create_parent_invocation_context(
      request.function.__name__, sub_agent
  )

  events = [e async for e in sub_agent.run_async(parent_ctx)]

  assert len(events) == 1
  assert events[0].get_function_calls()[0].name == "transfer_to_agent"
  assert (
      events[0].get_function_calls()[0].args["agent_name"]
      == parent.name
  )


def test_allow_transfer_by_default():
  sub_agent = LlmAgent(name="sub_agent")
  agent = LlmAgent(name="test_agent", sub_agents=[sub_agent])

  assert not agent.disallow_transfer_to_parent
  assert not agent.disallow_transfer_to_peers