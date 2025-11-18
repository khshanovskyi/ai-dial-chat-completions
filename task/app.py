import asyncio

from task.clients.client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    client = DialClient(
        deployment_name="gpt-4o",
    )

    conversation = Conversation()

    print("Provide System prompt or press 'enter' to continue.")

    prompt = input("> ").strip()

    if prompt:
        conversation.add_message(Message(Role.SYSTEM, prompt))
        print("System prompt successfully added to conversation.")
    else:
        conversation.add_message(Message(Role.SYSTEM, DEFAULT_SYSTEM_PROMPT))
        print(
            f"No System prompt provided. Will be used default System prompt: '{DEFAULT_SYSTEM_PROMPT}'"
        )

    print("Type your question or 'exit' to quit.")

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break

        conversation.add_message(Message(Role.USER, user_input))

        print("AI:")
        if stream:
            ai_message = await client.stream_completion(conversation.get_messages())
        else:
            ai_message = client.get_completion(conversation.get_messages())

        conversation.add_message(ai_message)
        print(f"AI: {ai_message.content}")


asyncio.run(start(True))
