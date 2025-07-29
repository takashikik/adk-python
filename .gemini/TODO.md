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
* unittestは全部実行すると時間がかかるので、**極力、必要なtestのみ実行し**、最後に念の為全部実行というように
* **src/google/adk/runners.pyの部分など,コアな部分は極力修正してはいけない,本当の本当に最後の手段**


## P1
- [ ] 下記のIssueへの対応(サブタスクに分けて対応)
src/google/adk/agents/llm_agent_config.py
src/google/adk/agents/llm_agent.py
への反映は完了済み
```
Currently, the Agent has a disallow_transfer_to_parent setting to prevent transferring control to the parent agent. However, there are scenarios where the opposite behavior is desired: forcing the agent to always transfer control back to its parent. Without this feature, it's difficult to ensure that a child agent reliably returns to the parent's context after completing its task.

Describe the solution you'd like
I propose adding a new boolean property to the Agent, named enforce_transfer_to_parent.

When enforce_transfer_to_parent is set to True, the agent must transfer control to its parent agent after its execution is complete. This would act as the inverse of disallow_transfer_to_parent.

Describe alternatives you've considered
One could manually implement a transfer to the parent at the end of every tool within the agent. However, this approach is repetitive and error-prone. A dedicated property on the agent itself would provide a cleaner, more declarative, and more reliable way to manage the conversation flow.

Additional context
This feature would be particularly useful for creating hierarchical agent structures. For example, a parent agent could delegate a specific, self-contained task to a child agent, and with this new property, it can be guaranteed that the conversation flow returns to the parent to continue the main process. This provides more robust control over agent routing.

---参考: 現状この実装をしなくてもCallbackで同等のことを実現できる.ただCallbackの部分の処理に修正を入れるのではなく, 

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
```
注意:  callback周りの修正ではなく,@src/google/adk/flows/llm_flows/agent_transfer.py を修正する形での実装にする必要がある
```参考
このenforce_transfer_to_parent機能を実装するには、以下のコード箇所を修正する必要があります：

1. LlmAgentクラスへのプロパティ追加
LlmAgentクラスに新しいenforce_transfer_to_parentプロパティを追加する必要があります。既存のdisallow_transfer_to_parentとdisallow_transfer_to_peersプロパティの近くに配置するのが適切です。 llm_agent.py:156-166

2. LlmAgentConfigクラスへの設定項目追加
YAML設定ファイルからの設定をサポートするため、LlmAgentConfigクラスにも対応するフィールドを追加する必要があります。 llm_agent_config.py:48-52

3. 設定ロード処理の修正
from_configメソッドで新しい設定項目を読み込む処理を追加する必要があります。 llm_agent.py:572-575

4. フロー完了後の自動転送ロジック実装
最も重要な修正箇所は、エージェントの実行完了時に親エージェントへの自動転送を行う処理です。これはBaseLlmFlowクラスの実行完了ロジックに実装する必要があります。 base_llm_flow.py:492-507

5. 転送対象の決定ロジックの修正
現在の転送対象を決定する_get_transfer_targets関数では、disallow_transfer_to_parentをチェックしていますが、enforce_transfer_to_parentの場合は異なるロジックが必要になる可能性があります。 agent_transfer.py:113-132

6. バリデーション処理の追加
enforce_transfer_to_parentがdisallow_transfer_to_parentと競合しないよう、適切なバリデーション処理を追加する必要があります。既存の__check_output_schemaメソッドと同様の検証ロジックが必要です。 llm_agent.py:476-504

実装のポイント
enforce_transfer_to_parent=Trueの場合、エージェントの実行完了時に自動的に親エージェントに制御を移すロジックが必要
disallow_transfer_to_parent=Trueとenforce_transfer_to_parent=Trueの同時設定は論理的に矛盾するため、バリデーションエラーとする
output_schemaが設定されている場合との整合性も確認が必要
Notes
この機能は既存のdisallow_transfer_to_parentの逆の動作を提供しますが、実装上は単純な反転ではありません。disallow_transfer_to_parentは転送能力を制限する設定ですが、enforce_transfer_to_parentは実行完了後の自動転送を強制する設定であり、フローの異なる段階で動作します。特に、エージェントの実行が完了した時点で親エージェントへの転送を自動的に実行する仕組みを新たに実装する必要があります。
```
    ### サブタスク
    - [ ] 修正する箇所を決めるための徹底的なソースコードの読み込み
    - [ ] 修正方針を明文化しTIPS.mdへ記載
    - [ ] 修正方針に従っての実装

- [ ] この修正の影響が他のテストケースに影響問題ないか, unittest(tests/unittests)を行い、影響あれば必要に応じてコードまたはテストコードの修正を行って
- [ ] この修正に関するunittest(tests/unittests)を追加し,動作が問題ないか検証して,その場合に既存のコードファイルを大幅に変更したりしてはいけない
- [ ] この修正の影響が問題ないか, type checkを行って
- [ ] すべてのtestがpassするか,再度 unittest(tests/unittests)を行って
- [ ] この修正のPR Messageを.gemini/WORK配下に作って
- [ ] GEMINI.mdに従って.gemini/*配下のドキュメントをすべて更新
- [ ] Integration テスト用の超簡単なsample agent.pyを作って