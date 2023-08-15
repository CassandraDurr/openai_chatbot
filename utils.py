"""A module storing helper functions."""
import json
import openai


# Return the API key from the configurations json file
def get_api_key(config_location: str = "config.json"):
    """Return the OpenAi API key stored in a json file.

    Args:
        config_location (str, optional): String location of the configurations file. Defaults to "config.json".

    Returns:
        str: stored API key
    """
    with open(config_location, "r") as config_file:
        config_data = json.load(config_file)

    return config_data["api_key"]


# Define the characteristics of a given chatbot.
# Source of inspiration: https://ihsavru.medium.com/how-to-build-your-own-custom-chatgpt-using-python-openai-78e470d1540e
class Chatbot:
    """A class defining a chatbot and code for user-chatbot interactions."""

    def __init__(
        self, name: str, personality: str, start_prompt: str, exit_cue: str = "EXIT"
    ) -> None:
        """Initialise a Chatbot instance.

        Args:
            name (str): The name of the chatbot.
            personality (str): A description of the chatbot's intended personality.
            start_prompt (str): The text presented at the start of a conversation with the chatbot.
            exit_cue (str, optional): The user prompt ending the conversation with the chatbot. Defaults to "EXIT".
        """
        self.name = name
        self.messages = [{"role": "system", "content": personality}]
        self.start_prompt = start_prompt
        self.exit_cue = exit_cue

    def generate_response(
        self, user_input: str, model_gen: str = "gpt-3.5-turbo"
    ) -> str:
        """This function returns a string response from the chatbot given user input.

        Args:
            user_input (str): User inputted text.
            model_gen (str, optional): The ID of the model to use. Model ID's are given at https://platform.openai.com/docs/models/how-we-use-your-data
            Defaults to "gpt-3.5-turbo".

        Returns:
            str: Chatbot's text response to user input.
        """
        # Append user input to messages list
        self.messages.append({"role": "user", "content": user_input})

        # Request model's response for chat completion
        response = openai.ChatCompletion.create(model=model_gen, messages=self.messages)

        # Extract and return chatbot's response to user input
        chatbot_reply = response["choices"][0]["message"]["content"]

        # Append chatbot's response to messages list
        self.messages.append({"role": "assistant", "content": chatbot_reply})
        return f"{self.name}: {chatbot_reply}"

    def run_chat(self, model_gen: str = "gpt-3.5-turbo") -> None:
        """Run a conversation between a user and the initialised chatbot until the exit cue is triggered.

        Args:
            model_gen (str, optional): The ID of the model to use. Model ID's are given at https://platform.openai.com/docs/models/how-we-use-your-data
            Defaults to "gpt-3.5-turbo".
        """
        # Print the starting prompt to the program
        print(f"{self.name}: {self.start_prompt}")

        while True:
            # Prompt user for input
            user_input = input("You: ")

            # Break while loop if exit cue triggered.
            if user_input == self.exit_cue:
                print(f"{self.name}: See you next time.")
                break

            # Print the chatbot's response
            print(self.generate_response(user_input, model_gen))
