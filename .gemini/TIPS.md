## `enforce_transfer_to_parent`のテスト

`enforce_transfer_to_parent`が設定されたエージェントのテストを行う場合、`runner.run()`を呼び出す前に、セッションの`current_agent_name`を対象のエージェントに設定する必要がある。しかし、`runners.py`は変更すべきではないため、`session.state['current_agent_name']`を直接設定するのではなく、`runner.run_async`を呼び出す際に`current_agent_name`を引数として渡すことで、テストが可能である。

また、`runner.run_async`を呼び出す前に、対象のエージェントからのダミーイベントをセッションに追加することで、`_find_agent_to_run`が対象のエージェントを返すように仕向けることができる。
