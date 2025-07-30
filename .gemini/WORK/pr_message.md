# feat: Add fallback_to_parent functionality to LlmAgent

## Summary

This PR implements the `fallback_to_parent` feature for `LlmAgent`, which allows agents to automatically transfer control back to their parent agent after completing their execution. This provides a declarative way to ensure that child agents reliably return to the parent's context after completing their tasks.

## Key Changes

### Core Implementation
- **LlmAgentConfig**: Added `fallback_to_parent` property to support configuration
- **LlmAgent**: Added `fallback_to_parent` boolean field with comprehensive documentation
- **BaseLlmFlow**: Implemented fallback logic in both `_postprocess_async` and `_postprocess_live` methods

### Fallback Behavior Logic
The fallback behavior is only activated when no model transfer occurs. Fallback to parent only happens when:
- The agent is an LlmAgent instance
- `fallback_to_parent=True`
- `parent_agent` exists
- The model response contains no function calls (indicating no `transfer_to_agent`)

### Test Coverage
Added comprehensive test suite in `tests/unittests/flows/llm_flows/test_enforce_transfer.py`:
-  Basic fallback functionality
-  No fallback when model already has transfer calls
-  No fallback when `fallback_to_parent=False`
-  No fallback when no parent agent exists
-  No fallback for non-LlmAgent instances
-  Multi-level hierarchy fallback cascading
-  Live mode functionality

## Behavior Details

When `fallback_to_parent=True`, the agent will:
1. Execute normally and generate its response
2. If no function calls (including `transfer_to_agent`) are present in the response
3. Automatically create a `transfer_to_agent` function call to the parent
4. Transfer execution to the parent agent

This is particularly useful for creating hierarchical agent structures where:
- A parent agent delegates specific, self-contained tasks to child agents
- The conversation flow is guaranteed to return to the parent to continue the main process
- More robust control over agent routing is achieved

## Breaking Changes
None. This is a purely additive feature with default value `False`.

## Testing
- All existing tests pass without regression
- New comprehensive test suite covers edge cases and integration scenarios
- Live mode functionality verified

> Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>