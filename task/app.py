import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    #TODO:
    # 1.1. Create DialClient
    # (you can get available deployment_name via https://ai-proxy.lab.epam.com/openai/models
    #  you can import Postman collection to make a request, file in the project root `dial-basics.postman_collection.json`
    #  don't forget to add your API_KEY)
    # 1.2. Create CustomDialClient
    # 2. Create Conversation object
    # 3. Get System prompt from console or use default -> constants.DEFAULT_SYSTEM_PROMPT and add to conversation
    #    messages.
    # 4. Use infinite cycle (while True) and get yser message from console
    # 5. If user message is `exit` then stop the loop
    # 6. Add user message to conversation history (role 'user')
    # 7. If `stream` param is true -> call DialClient#stream_completion()
    #    else -> call DialClient#get_completion()
    # 8. Add generated message to history
    # 9. Test it with DialClient and CustomDialClient
    # 10. In CustomDialClient add print of whole request and response to see what you send and what you get in response

    client = DialClient('gpt-4o')
    customClient = CustomDialClient('gpt-4o')

    conversation = Conversation()

    print("Provide System prompt or press 'enter' to continue.")
    prompt = input("> ").strip()

    if prompt:
        conversation.add_message(Message(Role.SYSTEM, prompt))
    else:
        conversation.add_message(Message(Role.SYSTEM, DEFAULT_SYSTEM_PROMPT))

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == "exit":
            break

        conversation.add_message(Message(Role.USER, user_input))

        if stream:
            ai_response = await customClient.stream_completion(conversation.get_messages())
        else:
            ai_response = customClient.get_completion(conversation.get_messages())

    conversation.add_message(ai_response)

asyncio.run(
    start(False)
)
