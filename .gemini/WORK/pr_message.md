
feat: add enforce_transfer_to_parent to LlmAgent

This adds a new boolean property to the `LlmAgent` named `enforce_transfer_to_parent`.

When `fallback_to_parent` is set to `True`, the agent must transfer control to its parent agent after its execution is complete. This acts as the inverse of `disallow_transfer_to_parent`.

This feature is useful for creating hierarchical agent structures. For example, a parent agent could delegate a specific, self-contained task to a child agent, and with this new property, it can be guaranteed that the conversation flow returns to the parent to continue the main process. This provides more robust control over agent routing.

#non-breaking
