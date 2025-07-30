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
- [x] 下記のfallback_to_parent追加のIssueへの対応(サブタスクに分けて対応)
少なくとも
src/google/adk/agents/llm_agent_config.py
src/google/adk/agents/llm_agent.py
src/google/adk/flows/llm_flows/base_llm_flow.py
への反映が必要
```
Currently, the Agent has a disallow_transfer_to_parent setting to prevent transferring control to the parent agent. However, there are scenarios where the opposite behavior is desired: forcing the agent to always transfer control back to its parent. Without this feature, it's difficult to ensure that a child agent reliably returns to the parent's context after completing its task.

Describe the solution you'd like
I propose adding a new boolean property to the Agent, named fallback_to_parent.

When fallback_to_parent is set to True, the agent must transfer control to its parent agent after its execution is complete. This would act as the inverse of disallow_transfer_to_parent.

Describe alternatives you've considered
One could manually implement a transfer to the parent at the end of every tool within the agent. However, this approach is repetitive and error-prone. A dedicated property on the agent itself would provide a cleaner, more declarative, and more reliable way to manage the conversation flow.

Additional context
This feature would be particularly useful for creating hierarchical agent structures. For example, a parent agent could delegate a specific, self-contained task to a child agent, and with this new property, it can be guaranteed that the conversation flow returns to the parent to continue the main process. This provides more robust control over agent routing.

- [x] tests/unittests/flows/llm_flows/test_enforce_transfer.pyへのテストケースの追加。
特に必要なテストケース
1. parent_agentが存在しない場合のテスト
fallback_to_parent=Trueだがparent_agentが設定されていない場合の動作をテストする必要があります llm_agent.py:157-163 。

@pytest.mark.asyncio  
async def test_fallback_to_parent_without_parent_agent():  
    """Tests behavior when fallback_to_parent is True but no parent_agent exists."""  
    child_agent = LlmAgent(  
        name="child",  
        model=MockModel.create(responses=["Response from child"]),  
        fallback_to_parent=True,  
    )  
    # parent_agentが設定されていない状態でのテスト
2. モデルが既にファンクションコールを返している場合のテスト
モデルレスポンスに既にファンクションコールが含まれている場合、強制転送が実行されないことを確認する必要があります。これは実装の第1段階の条件 not model_response_event.get_function_calls() に対応します 。

3. 非LlmAgentでのテスト
isinstance(agent, LlmAgent) の条件をテストするため、非LlmAgentでの動作確認が必要です test_runners.py:34-56 。

4. ライブモードでのテスト
現在のテストは _run_one_step_async のみをテストしていますが、ライブモード（_postprocess_live）での動作もテストすべきです base_llm_flow.py:454-467 。

- [x] 今回の修正のリファクタリング

- [x] 以下の内容をコメントの必要な所や, pull request message(.gemini/WORK/pr_message.md)に追加
フォールバック動作は、モデル転送が発生しない場合にのみアクティブになります。親へのフォールバックは、次の場合にのみ発生します。
エージェントはLlmAgentインスタンスである
fallback_to_parent=True
parent_agent存在する
かつ、モデル応答にtransfer to agentを含め、関数呼び出しが含まれていない()
- [x] src/google/adk/agents/llm_agent.pyのfallback_to_parentの説明文をより詳細に記載
- [x] この修正の影響が他のテストケースに影響問題ないか, unittest(tests/unittests)を行い、影響あれば必要に応じてコードまたはテストコードの修正を行って
- [x] この修正に関するunittest(tests/unittests)を追加し,動作が問題ないか検証して,その場合に既存のコードファイルを大幅に変更したりしてはいけない
- [x] この修正の影響が問題ないか, type checkを行って
- [x] すべてのtestがpassするか,再度 unittest(tests/unittests)を行って
- [x] この修正のPR Messageを.gemini/WORK配下に作って
- [x] GEMINI.mdに従って.gemini/*配下のドキュメントをすべて更新
- [ ] 今回のこの修正に対しての徹底的なコードレビューを実施し、修正必要あれば修正を進めて