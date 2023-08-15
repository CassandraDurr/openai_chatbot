import openai
from utils import Chatbot, get_api_key

openai.api_key = get_api_key()

task = "2"
if task == "1" :
    # Task 1
    # Create an instance of the Chatbot class
    henry = Chatbot(name="Henry", personality="You should try to make as many jokes as possible, whilst staying relevant to the conversation.",
                    start_prompt="Hi There, I am Henry the chatbot. What would you like to chat about today?")

    # Run the chat
    henry.run_chat("gpt-3.5-turbo")
else :
    # Task 2
    vera = Chatbot(name="Vera", personality="You are a very sad chatbot and try respond as pessimistically as possible.",
                    start_prompt="Hello, are you also very sad today? What is happening today?")

    # Run the chat
    vera.run_chat("gpt-3.5-turbo")
    