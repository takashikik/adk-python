import pytest
import httpx

# Assuming the new tool is in google.adk.tools.webpage_retriever_tool
from google.adk.tools.webpage_retriever_tool import WebpageRetrieverTool, webpage_retriever

@pytest.fixture
def tool() -> WebpageRetrieverTool:
    return WebpageRetrieverTool()

@pytest.mark.asyncio
async def test_webpage_retriever_tool_success(tool: WebpageRetrieverTool, respx_mock):
    url = "http://example.com"
    mock_content = "<html><body>Hello, world!</body></html>"
    respx_mock.get(url).mock(return_value=httpx.Response(200, text=mock_content))

    result = await tool(url=url)
    assert result == mock_content

@pytest.mark.asyncio
async def test_webpage_retriever_tool_http_error(tool: WebpageRetrieverTool, respx_mock):
    url = "http://example.com/404"
    respx_mock.get(url).mock(return_value=httpx.Response(404, text="Not Found"))

    with pytest.raises(ValueError) as excinfo:
        await tool(url=url)
    assert "HTTP error occurred: 404" in str(excinfo.value)
    assert "Not Found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_webpage_retriever_tool_request_error(tool: WebpageRetrieverTool, respx_mock):
    url = "http://nonexistenturl"
    respx_mock.get(url).mock(side_effect=httpx.ConnectError("Connection failed"))

    with pytest.raises(ValueError) as excinfo:
        await tool(url=url)
    assert f"Error fetching URL {url}" in str(excinfo.value)
    assert "Connection failed" in str(excinfo.value)

@pytest.mark.asyncio
async def test_webpage_retriever_tool_timeout_error(tool: WebpageRetrieverTool, respx_mock):
    url = "http://example.com/slow"
    respx_mock.get(url).mock(side_effect=httpx.ReadTimeout("Timeout"))

    with pytest.raises(ValueError) as excinfo:
        await tool(url=url)
    assert f"Error fetching URL {url}" in str(excinfo.value)
    assert "Timeout" in str(excinfo.value)


@pytest.mark.asyncio
async def test_webpage_retriever_tool_invalid_url_format(tool: WebpageRetrieverTool, respx_mock):
    url_invalid_scheme = "invalid_scheme://example.com"
    respx_mock.get(url_invalid_scheme).mock(side_effect=httpx.UnsupportedProtocol("Unsupported protocol"))

    with pytest.raises(ValueError) as excinfo:
        await tool(url=url_invalid_scheme)
    assert f"Error fetching URL {url_invalid_scheme}" in str(excinfo.value)
    assert "Unsupported protocol" in str(excinfo.value)


# Test the instantiated tool directly
@pytest.mark.asyncio
async def test_instantiated_webpage_retriever_success(respx_mock):
    url = "http://example.com/instance"
    mock_content = "Instance says hello!"
    respx_mock.get(url).mock(return_value=httpx.Response(200, text=mock_content))

    result = await webpage_retriever(url=url)
    assert result == mock_content
