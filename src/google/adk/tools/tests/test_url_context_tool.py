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

import pytest
from google.genai import types

from google.adk.models import LlmRequest
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.url_context_tool import UrlContextTool, url_context


@pytest.fixture
def llm_request_empty() -> LlmRequest:
  """Returns an empty LlmRequest."""
  return LlmRequest(invocations=[])


@pytest.fixture
def llm_request_with_model() -> LlmRequest:
  """Returns an LlmRequest with a supported model."""
  return LlmRequest(invocations=[], model="gemini-2.5-flash-preview-05-20")


@pytest.fixture
def llm_request_with_unsupported_model() -> LlmRequest:
  """Returns an LlmRequest with an unsupported model."""
  return LlmRequest(invocations=[], model="gemini-1.0-pro")


@pytest.fixture
def tool_context_mock() -> ToolContext:
  """Returns a mock ToolContext."""
  return ToolContext(
      user_tool_params={},
      user_tool_logs=[],
      history_user_tool_params=[],
      history_user_tool_logs=[],
      memories=[],
  )


@pytest.mark.asyncio
async def test_url_context_tool_instance_exists():
  """Tests that the url_context instance is available."""
  assert isinstance(url_context, UrlContextTool)
  assert url_context.name == "url_context"
  assert (
      url_context.description
      == "Enables the model to use content from provided URLs as context."
  )


@pytest.mark.asyncio
async def test_process_llm_request_adds_tool_when_config_is_none(
    llm_request_with_model: LlmRequest, tool_context_mock: ToolContext
):
  """Tests that UrlContext is added when LlmRequest.config is None."""
  assert llm_request_with_model.config is None
  await url_context.process_llm_request(
      tool_context=tool_context_mock, llm_request=llm_request_with_model
  )
  assert llm_request_with_model.config is not None
  assert llm_request_with_model.config.tools is not None
  assert len(llm_request_with_model.config.tools) == 1
  added_tool = llm_request_with_model.config.tools[0]
  assert isinstance(added_tool.url_context, types.UrlContext)


@pytest.mark.asyncio
async def test_process_llm_request_adds_tool_when_tools_is_none(
    llm_request_with_model: LlmRequest, tool_context_mock: ToolContext
):
  """Tests that UrlContext is added when LlmRequest.config.tools is None."""
  llm_request_with_model.config = types.GenerateContentConfig()
  assert llm_request_with_model.config.tools is None
  await url_context.process_llm_request(
      tool_context=tool_context_mock, llm_request=llm_request_with_model
  )
  assert llm_request_with_model.config.tools is not None
  assert len(llm_request_with_model.config.tools) == 1
  added_tool = llm_request_with_model.config.tools[0]
  assert isinstance(added_tool.url_context, types.UrlContext)


@pytest.mark.asyncio
async def test_process_llm_request_adds_tool_to_existing_tools(
    llm_request_with_model: LlmRequest, tool_context_mock: ToolContext
):
  """Tests that UrlContext is added to an existing list of tools."""
  existing_tool = types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())
  llm_request_with_model.config = types.GenerateContentConfig(
      tools=[existing_tool]
  )
  await url_context.process_llm_request(
      tool_context=tool_context_mock, llm_request=llm_request_with_model
  )
  assert llm_request_with_model.config.tools is not None
  assert len(llm_request_with_model.config.tools) == 2
  assert llm_request_with_model.config.tools[0] == existing_tool
  added_tool = llm_request_with_model.config.tools[1]
  assert isinstance(added_tool.url_context, types.UrlContext)


@pytest.mark.asyncio
async def test_process_llm_request_does_not_add_duplicate_tool(
    llm_request_with_model: LlmRequest, tool_context_mock: ToolContext
):
  """Tests that UrlContext is not added if already present."""
  existing_url_tool = types.Tool(url_context=types.UrlContext())
  llm_request_with_model.config = types.GenerateContentConfig(
      tools=[existing_url_tool]
  )
  await url_context.process_llm_request(
      tool_context=tool_context_mock, llm_request=llm_request_with_model
  )
  assert llm_request_with_model.config.tools is not None
  assert len(llm_request_with_model.config.tools) == 1
  assert llm_request_with_model.config.tools[0] == existing_url_tool


@pytest.mark.asyncio
async def test_process_llm_request_raises_error_for_unsupported_model(
    llm_request_with_unsupported_model: LlmRequest,
    tool_context_mock: ToolContext,
):
  """Tests that ValueError is raised for unsupported models."""
  with pytest.raises(ValueError) as excinfo:
    await url_context.process_llm_request(
        tool_context=tool_context_mock,
        llm_request=llm_request_with_unsupported_model,
    )
  assert "URL context tool is not supported for model gemini-1.0-pro" in str(
      excinfo.value
  )
  assert llm_request_with_unsupported_model.config is None # Config should not be modified


@pytest.mark.asyncio
async def test_process_llm_request_no_error_if_model_is_none(
    llm_request_empty: LlmRequest, tool_context_mock: ToolContext
):
  """Tests no error if model is None (model check is skipped)."""
  assert llm_request_empty.model is None
  await url_context.process_llm_request(
      tool_context=tool_context_mock, llm_request=llm_request_empty
  )
  assert llm_request_empty.config is not None
  assert len(llm_request_empty.config.tools) == 1
  assert isinstance(
      llm_request_empty.config.tools[0].url_context, types.UrlContext
  )

# Example of a supported model not explicitly in the fixture
@pytest.mark.asyncio
async def test_process_llm_request_supported_model_variant(
    tool_context_mock: ToolContext
):
  """Tests with another supported model variant."""
  llm_request = LlmRequest(invocations=[], model="gemini-2.0-flash-live-001")
  await url_context.process_llm_request(
      tool_context=tool_context_mock, llm_request=llm_request
  )
  assert llm_request.config is not None
  assert len(llm_request.config.tools) == 1
  assert isinstance(
      llm_request.config.tools[0].url_context, types.UrlContext
  )
