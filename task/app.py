import asyncio
from task.clients.client import DialClient
from task.clients.custom_client import CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    deployment_name = "gpt-4"

    # Initialize both clients
    dial_client = DialClient(deployment_name)
    custom_client = CustomDialClient(deployment_name)

    # Let user choose client
    try:
        client_type = input("Choose client (1=DialClient, 2=CustomDialClient): ").strip() or "1"
    except EOFError:
        print("No input provided. Defaulting to DialClient.")
        client_type = "1"

    client = dial_client if client_type == "1" else custom_client

    conversation = Conversation()
    try:
        system_prompt = input(f"System prompt (default: {DEFAULT_SYSTEM_PROMPT}): ").strip() or DEFAULT_SYSTEM_PROMPT
    except EOFError:
        print("No input provided. Using default system prompt.")
        system_prompt = DEFAULT_SYSTEM_PROMPT

    conversation.add_message(Message(Role.SYSTEM, system_prompt))

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except EOFError:
            print("\nNo input provided. Exiting...")
            break

        if user_input.lower() == 'exit':
            break

        conversation.add_message(Message(Role.USER, user_input))

        try:
            if stream:
                print("AI: ", end='', flush=True)
                response = await client.stream_completion(conversation.get_messages())
            else:
                response = client.get_completion(conversation.get_messages())
                print("\nAI:", response.content)

            conversation.add_message(response)
        except Exception as e:
            print(f"\nError: {e}")

    print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(start(True))
