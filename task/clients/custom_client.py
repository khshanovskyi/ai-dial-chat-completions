import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # Take a look at README.md of how the request and regular response are looks like!
        # 1. Create headers dict with api-key and Content-Type
        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        # 4. Get content from response, print it and return message with assistant role and content
        # 5. If status code != 200 then raise Exception with format: f"HTTP {response.status_code}: {response.text}"

        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }

        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }
        
        response = requests.post(self._endpoint, headers=headers, json=request_data)

        if response.status_code == 200:
            data = response.json()
            choices = data.get('choices', [])
            if choices and len(choices) > 0:
                content = choices[0]["message"]["content"]
                print(content)
                return Message(Role.AI, content)
            
            raise ValueError("No Choice has been present in the response")

        raise Exception(f"HTTP {response.status_code}: {response.text}")

    async def stream_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # Take a look at README.md of how the request and streamed response chunks are looks like!
        # 1. Create headers dict with api-key and Content-Type
        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Create empty list called 'contents' to store content snippets
        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        # 5. Inside session, make POST request using session.post() with:
        #    - URL: self._endpoint
        #    - json: request_data from step 2
        #    - headers: headers from step 1
        #    - Use 'async with' context manager for response
        # 6. Get content from chunks (don't forget that chunk start with `data: `, final chunk is `data: [DONE]`), print
        #    chunks, collect them and return as assistant message

        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        request_data = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
        }
        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url=self._endpoint, headers=headers, json=request_data) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data = line_str[6:].strip()
                            if data != "[DONE]":
                                content_snippet = self._get_content_snippet(data)
                                print(content_snippet, end='')
                                contents.append(content_snippet)
                            else:
                                print()
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")
                return Message(role=Role.AI, content=''.join(contents))
            
    def _get_content_snippet(self, data: str) -> str:
        data = json.loads(data)
        if choices := data.get("choices"):
            delta = choices[0].get("delta", {})
            return delta.get("content", '')
        return ''

