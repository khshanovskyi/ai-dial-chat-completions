import json
import aiohttp
import requests
from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class CustomDialClient(BaseClient):
    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = f"{DIAL_ENDPOINT}/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            'Api-Key': self._api_key,
            'Content-Type': 'application/json'
        }
        request_data = {
            'messages': [msg.to_dict() for msg in messages]
        }
        response = requests.post(self._endpoint, headers=headers, json=request_data)

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        response_data = response.json()
        if not response_data.get('choices'):
            raise Exception("No choices in response found")

        content = response_data['choices'][0]['message']['content']
        print(content)
        return Message(Role.AI, content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            'Api-Key': self._api_key,
            'Content-Type': 'application/json'
        }
        request_data = {
            'messages': [msg.to_dict() for msg in messages],
            'stream': True
        }
        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, headers=headers, json=request_data) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"HTTP {response.status}: {text}")

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and chunk['choices']:
                                content = chunk['choices'][0]['delta'].get('content', '')
                                if content:
                                    print(content, end='', flush=True)
                                    contents.append(content)
                        except json.JSONDecodeError:
                            pass

        print()
        return Message(Role.AI, ''.join(contents))