# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents.llm_agent import Agent
from google.genai.types import Part

from ... import testing_utils


def transfer_call_part(agent_name: str) -> Part:
  return Part.from_function_call(
      name='transfer_to_agent', args={'agent_name': agent_name}
  )


TRANSFER_RESPONSE_PART = Part.from_function_response(
    name='transfer_to_agent', response={'result': None}
)


def test_enforce_transfer_to_parent():
  response = [
      transfer_call_part('sub_agent_1'),
      transfer_call_part('root_agent'),
      'response1',
  ]
  mockModel = testing_utils.MockModel.create(responses=response)
  # root (auto) - sub_agent_1 (auto)
  sub_agent_1 = Agent(
      name='sub_agent_1',
      model=mockModel,
      enforce_transfer_to_parent=True,
  )
  root_agent = Agent(
      name='root_agent',
      model=mockModel,
      sub_agents=[sub_agent_1],
  )

  runner = testing_utils.InMemoryRunner(root_agent)

  # Asserts the transfer.
  assert testing_utils.simplify_events(runner.run('test1')) == [
      ('root_agent', transfer_call_part('sub_agent_1')),
      ('root_agent', TRANSFER_RESPONSE_PART),
      ('sub_agent_1', transfer_call_part('root_agent')),
      ('sub_agent_1', TRANSFER_RESPONSE_PART),
      ('root_agent', 'response1'),
  ]
