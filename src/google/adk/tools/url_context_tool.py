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

from __future__ import annotations

from typing import TYPE_CHECKING

from google.genai import types
from typing_extensions import override

from .base_tool import BaseTool
from .tool_context import ToolContext

if TYPE_CHECKING:
  from ..models import LlmRequest


class UrlContextTool(BaseTool):
  """A tool to enable URL context fetching for Gemini models.

  This tool configures the LLM request to allow the model to retrieve content
  from URLs provided in the prompt and use that content to inform its response.
  """

  def __init__(self):
    super().__init__(
        name='url_context',
        description='Enables the model to use content from provided URLs as context.'
    )

  @override
  async def process_llm_request(
      self,
      *,
      tool_context: ToolContext,
      llm_request: LlmRequest,
  ) -> None:
    """Modifies the LLM request to include the URL context tool.

    Raises:
      ValueError: If the model does not support URL context.
    """
    # Supported models for URL context (based on documentation)
    # https://ai.google.dev/gemini-api/docs/url-context#supported_models
    supported_models = [
        "gemini-2.5-pro-preview-05-06",
        "gemini-2.5-flash-preview-05-20",
        "gemini-2.0-flash",
        "gemini-2.0-flash-live-001",
    ]

    if llm_request.model and not any(
        supported_model_name in llm_request.model for supported_model_name in supported_models
    ):
      raise ValueError(
          f"URL context tool is not supported for model {llm_request.model}. "
          f"Supported models are: {', '.join(supported_models)}"
      )

    llm_request.config = llm_request.config or types.GenerateContentConfig()
    llm_request.config.tools = llm_request.config.tools or []

    # Check if UrlContext is already added to avoid duplicates.
    # This can happen if the user adds it manually or if another tool also adds it.
    # Note: The genai library might already handle deduplication, but an explicit check is safer.
    if not any(tool.url_context is not None for tool in llm_request.config.tools):
        llm_request.config.tools.append(
            types.Tool(url_context=types.UrlContext())
        )


url_context = UrlContextTool()
