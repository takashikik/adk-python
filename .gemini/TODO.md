# ADK Studio - TODO List

このファイルは、開発の進捗と今後のタスクを管理するためのものです。

## 前提事項
* **必ず一つTaskを実施する際には,TDD(unittestを作成してから作業)で作業を進めて行ってください**
* **TODOの作業は1タスクずつ実施し、完了後TODOを変更してから次のTaskに移ってください**
* **何回か同じファイルの編集に失敗する場合、そのファイルを削除して、作り直して**
* **pythonのpathは"/home/admin_takak_altostrat_com/projects/adk-python/.venv/bin/python"**
* まず作業の前にAGENTS.mdをかならずREADFIleすること
* unittestは" pytest ./tests/unittests"で実行可能
* Geminiの最新モデルは "gemini-2.5-pro", 1.5 ,2.0 ではない
* 1タスク

## P1
- [x] Is your feature request related to a problem? Please describe.
Currently, the Agent has a disallow_transfer_to_parent setting to prevent transferring control to the parent agent. However, there are scenarios where the opposite behavior is desired: forcing the agent to always transfer control back to its parent. Without this feature, it's difficult to ensure that a child agent reliably returns to the parent's context after completing its task.

Describe the solution you'd like
I propose adding a new boolean property to the Agent, named enforce_transfer_to_parent.

When enforce_transfer_to_parent is set to True, the agent must transfer control to its parent agent after its execution is complete. This would act as the inverse of disallow_transfer_to_parent.

Describe alternatives you've considered
One could manually implement a transfer to the parent at the end of every tool within the agent. However, this approach is repetitive and error-prone. A dedicated property on the agent itself would provide a cleaner, more declarative, and more reliable way to manage the conversation flow.

Additional context
This feature would be particularly useful for creating hierarchical agent structures. For example, a parent agent could delegate a specific, self-contained task to a child agent, and with this new property, it can be guaranteed that the conversation flow returns to the parent to continue the main process. This provides more robust control over agent routing.

I've been facing the same issue, and after trying various approaches, I found that creating the following Callback and adding it to the after_agent_callback of each child agent worked successfully for me.

def TransferToParentCallback(callback_context: CallbackContext):
    """
    A callback that always performs TransferToAgent to the parent Agent.
    """
    from google.genai import types
    current_agent = callback_context._invocation_context.agent
    if current_agent.parent_agent:
        return types.Content(
                    parts=[
                        types.Part(
                            function_call=types.FunctionCall(
                                name="transfer_to_agent",
                                args={"agent_name": current_agent.parent_agent.name}
                            )
                        )
                    ]
                )
 I believe the ideal solution would be for an enforce_transfer_to_parent feature to be implemented.
ただ,  callbackではなく,@src/google/adk/flows/llm_flows/agent_transfer.py を修正する形での実装にする必要がある
→すでにagent_transfer.pyに実装完了

- [ ] この修正の影響が他のテストケースに影響問題ないか, unittest(tests/unittests)を行い、影響あれば必要に応じてコードまたはテストコードの修正を行って
- [ ] この修正に関するunittest(tests/unittests)を追加し,動作が問題ないか検証して,その場合に既存のコードファイルを大幅に変更したりしてはいけない
- [ ] この修正の影響が問題ないか, type checkを行って
- [ ] すべてのtestがpassするか,再度 unittest(tests/unittests)を行って
- [ ] この修正のPR Messageを.gemini/WORK配下に作って