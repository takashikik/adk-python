import httpx
from typing_extensions import override
from google.adk.tools.base_tool import BaseTool, ToolCallMetadata

class WebpageRetrieverTool(BaseTool):
    def __init__(self):
        super().__init__(
            name='webpage_retriever',
            description='Fetches content from a URL.'
        )

    @override
    async def __call__(self, url: str, tool_call_metadata: ToolCallMetadata | None = None) -> str:
        # Implementation using httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={'User-Agent': 'ADK-Python-WebpageRetrieverTool/0.1'},
                    timeout=10.0,
                    follow_redirects=True
                )
                response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
                return response.text
        except httpx.HTTPStatusError as e:
            raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}") from e
        except httpx.RequestError as e:
            raise ValueError(f"Error fetching URL {url}: {e}") from e

webpage_retriever = WebpageRetrieverTool()
