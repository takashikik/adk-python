feat: Add enforce_transfer_to_parent to Agent

This adds a new boolean property to the `Agent` class, named `enforce_transfer_to_parent`.

When `enforce_transfer_to_parent` is set to `True`, the agent must transfer control to its parent agent after its execution is complete. This acts as the inverse of `disallow_transfer_to_parent`.

This feature is useful for creating hierarchical agent structures. For example, a parent agent can delegate a specific, self-contained task to a child agent, and with this new property, it can be guaranteed that the conversation flow returns to the parent to continue the main process. This provides more robust control over agent routing.

#non-breaking