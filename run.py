import openai
from utils import Chatbot, get_api_key

openai.api_key = get_api_key()

print("With whom would you like to chat today? \n[0] Henry \n[1] Vera")
user_input = input("You: ")

if user_input == "0":
    # Task 1
    henry = Chatbot(name="Henry", personality="You should try to make as many jokes as possible, whilst staying relevant to the conversation.",
                    start_prompt="Hi There, I am Henry the chatbot. What would you like to chat about today?")

    # Run the chat
    henry.run_chat("gpt-3.5-turbo")
    
elif user_input == "1":
    # Task 2
    vera = Chatbot(name="Vera", personality="You are a very sad chatbot and try respond as pessimistically as possible.",
                    start_prompt="Hello, are you also very sad today? What is happening today?")

    # Run the chat
    vera.run_chat("gpt-3.5-turbo")
else:
    raise ValueError("Invalid input. Please enter either 0 or 1.")
