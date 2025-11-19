from aidial_client import Dial, AsyncDial
from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        # Initialize Dial and AsyncDial clients with correct arguments
        self.client = Dial(
            base_url=DIAL_ENDPOINT,  # Base URL for the API
            api_key=self._api_key    # API key for authentication
        )
        self.async_client = AsyncDial(
            base_url=DIAL_ENDPOINT,  # Base URL for the API
            api_key=self._api_key    # API key for authentication
        )

    def get_completion(self, messages: list[Message]) -> Message:
        messages_dict = [msg.to_dict() for msg in messages]
        response = self.client.chat.completions.create(messages=messages_dict)
        if not response.choices:
            raise Exception("No choices in response found")
        content = response.choices[0].message.content
        print(content)
        return Message(Role.AI, content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        messages_dict = [msg.to_dict() for msg in messages]
        contents = []
        async for chunk in self.async_client.chat.completions.create(
            messages=messages_dict,
            stream=True
        ):
            content_chunk = chunk.choices[0].delta.content
            if content_chunk:
                print(content_chunk, end='', flush=True)
                contents.append(content_chunk)
        print()
        return Message(Role.AI, ''.join(contents))