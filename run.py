"""A module to run the chats with chatbots."""
import openai

from utils import Conversation, get_api_key

openai.api_key = get_api_key()
conversation = Conversation()
print(
    "What do you want to do? \n[0] continue a conversation \n[1] start a conversation"
)
user_input = input("You: ")

if user_input == "0":
    # Continue an existing conversation
    conversation.start_conversation_loader()
elif user_input == "1":
    # Start a new conversation
    conversation.start_new_conversation()
else:
    raise ValueError("Invalid input. Please enter either 0 or 1.")
