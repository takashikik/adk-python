
# `enforce_transfer_to_parent` Feature

This document describes the `fallback_to_parent` feature that was added to the `LlmAgent`.

## Overview

The `enforce_transfer_to_parent` is a boolean property on the `LlmAgent` that, when set to `True`, forces the agent to transfer control to its parent agent after its execution is complete. This feature is useful for creating hierarchical agent structures where it is desirable to ensure that a child agent reliably returns to the parent's context after completing its task.

## Implementation

The feature is implemented by modifying the `_postprocess_async` method in `base_llm_flow.py`. If an agent's `enforce_transfer_to_parent` property is set to `True` and the agent is about to generate a final response, the flow will instead generate a `transfer_to_agent` function call to the parent agent.

## Usage

To use this feature, set the `enforce_transfer_to_parent` property of an `LlmAgent` to `True`:

```python
child_agent = LlmAgent(
    name="child",
    model="gemini-2.5-pro",
    enforce_transfer_to_parent=True,
)
```
