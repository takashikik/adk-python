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
- [x] 下記のIssueへの対応(サブタスクに分けて対応)
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
    - [x] 修正する箇所を決めるための徹底的なソースコードの読み込み
    - [x] 修正方針を明文化しTIPS.mdへ記載
    - [x] 修正方針に従っての実装

- [x] この修正の影響が他のテストケースに影響問題ないか, unittest(tests/unittests)を行い、影響あれば必要に応じてコードまたはテストコードの修正を行って
- [x] この修正に関するunittest(tests/unittests)を追加し,動作が問題ないか検証して,その場合に既存のコードファイルを大幅に変更したりしてはいけない
- [x] この修正の影響が問題ないか, type checkを行って
- [x] すべてのtestがpassするか,再度 unittest(tests/unittests)を行って
- [x] この修正のPR Messageを.gemini/WORK配下に作って
- [x] GEMINI.mdに従って.gemini/*配下のドキュメントをすべて更新
- [ ] Integration テスト用の超簡単なsample agent.pyを作って

- [ ] src/google/adk/agents/llm_agent.pyの今回の修正に対する主要な問題点の修正
1. 重複したインポート文
from ...agents.llm_agent import LlmAgent
このインポート文が2回出現しています 。最初の条件分岐の前と、elseブロック内で再度インポートされています。これは不要な重複です。

2. 重複したロジック
第1段階と第2段階で同じ条件チェック（isinstance(agent, LlmAgent)、agent.enforce_transfer_to_parent、agent.parent_agent）が繰り返されています 。これはDRY原則に反しており、保守性を低下させます。

3. 複雑な制御フロー
2段階に分かれた処理により、同じ目的（親エージェントへの転送）を達成するために異なるパスが存在し、理解が困難です 。

改善提案
1. インポートの統一
ファイルの先頭で一度だけインポートし、関数内での重複インポートを削除する AGENTS.md:52-60 。

2. ヘルパー関数の抽出
共通の条件チェックと転送ロジックを別関数に抽出：

def _should_enforce_transfer_to_parent(self, agent) -> bool:  
    return (  
        isinstance(agent, LlmAgent)  
        and agent.enforce_transfer_to_parent  
        and agent.parent_agent  
    )  
  
def _create_transfer_function_call(self, agent):  
    return types.FunctionCall(  
        name='transfer_to_agent',  
        args={'agent_name': agent.parent_agent.name},  
    )
3. 単一責任の原則
現在の実装では、モデルレスポンスの修正と新しいイベントの作成という2つの異なるアプローチを使用しています。一貫性のために単一のアプローチに統一することを推奨します 。

- [ ] tests/unittests/flows/llm_flows/test_enforce_transfer.pyへのテストケースの追加。不足しているテストケース
1. parent_agentが存在しない場合のテスト
enforce_transfer_to_parent=Trueだがparent_agentが設定されていない場合の動作をテストする必要があります llm_agent.py:157-163 。

@pytest.mark.asyncio  
async def test_enforce_transfer_to_parent_without_parent_agent():  
    """Tests behavior when enforce_transfer_to_parent is True but no parent_agent exists."""  
    child_agent = LlmAgent(  
        name="child",  
        model=MockModel.create(responses=["Response from child"]),  
        enforce_transfer_to_parent=True,  
    )  
    # parent_agentが設定されていない状態でのテスト
2. モデルが既にファンクションコールを返している場合のテスト
モデルレスポンスに既にファンクションコールが含まれている場合、強制転送が実行されないことを確認する必要があります。これは実装の第1段階の条件 not model_response_event.get_function_calls() に対応します 。

3. 非LlmAgentでのテスト
isinstance(agent, LlmAgent) の条件をテストするため、非LlmAgentでの動作確認が必要です test_runners.py:34-56 。

4. ライブモードでのテスト
現在のテストは _run_one_step_async のみをテストしていますが、ライブモード（_postprocess_live）での動作もテストすべきです base_llm_flow.py:454-467 。

