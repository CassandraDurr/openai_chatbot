"""A module storing helper functions."""
import json
import re
from datetime import datetime
from pathlib import Path

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
        self,
        name: str,
        personality: str,
        start_prompt: str,
        prior_chat: list[dict] | None = None,
        store_conversation: bool = True,
        exit_cue: str = "EXIT",
        goodbye: str = "See you next time.",
    ) -> None:
        """Initialise a Chatbot instance.

        Args:
            name (str): The name of the chatbot.
            personality (str): A description of the chatbot's intended personality.
            start_prompt (str): The text presented at the start of a conversation with the chatbot.
            prior_chat (list[dict] | None, optional): _description_. Defaults to None.
            store_conversation (bool, optional): Whether the conversation statistics should be recorded and stored. Defaults to True.
            exit_cue (str, optional): The user prompt ending the conversation with the chatbot. Defaults to "EXIT".
            goodbye (str, optional): The sign-off message of the bot before the program is terminated. Defaults to "See you next time.".
        """
        self.name = name
        if prior_chat is None:
            self.messages = [{"role": "system", "content": personality}]
        else:
            self.messages = prior_chat
        self.start_prompt = start_prompt
        self.store_conversation = store_conversation
        self.exit_cue = exit_cue
        self.goodbye = goodbye

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
                print(f"{self.name}: {self.goodbye}")
                if self.store_conversation:
                    # Get the corresponding conversation statistics
                    conversation_statistics = self.get_conversation_statistics()
                    self.store_conversation_statistics(conversation_statistics)
                break

            # Print the chatbot's response
            print(self.generate_response(user_input, model_gen))

    def get_conversation_statistics(self) -> dict:
        """Return a dictionary of converation statistics upon exit cue tigger.

        Returns:
            dict: Conversation statistics including user and bot names, user characters, bot words and conversation topic.
        """

        # Extract user messages
        user_messages = [
            message["content"] for message in self.messages if message["role"] == "user"
        ]
        user_messages.append(self.exit_cue)

        # Extract conversation subject from the user's first message.
        subject = self.extract_conversation_topic(user_messages)

        # Extract the name of the user, if possible
        user_name = self.extract_user_name(user_messages)

        # Extract assistant messages
        bot_messages = [
            message["content"]
            for message in self.messages
            if message["role"] == "assistant"
        ]
        bot_messages.append(self.goodbye)
        bot_messages.insert(0, self.start_prompt)

        # Standardise the assistant messages to get the number of words
        # Replace \n with a space and remove punctuation
        processed_strings = [re.sub(r"\n", " ", string) for string in bot_messages]
        processed_strings = [
            re.sub(r"[^\w\s]", "", string) for string in processed_strings
        ]
        # Split the strings at whitespace characters
        processed_strings = [
            word for string in processed_strings for word in string.split()
        ]

        return {
            "Name of chatbot": self.name,
            "Number of characters typed by user": sum(
                len(string) for string in user_messages
            ),
            "Number of words used by chatbot": len(processed_strings),
            "Subject of conversation": subject,
            "Name of user": user_name,
            "Messages": self.messages,
        }

    def extract_user_name(self, user_messages: list[str]) -> str:
        """Extract the name of the user from user messages, if possible.

        Args:
            user_messages (list[str]): A list of messages typed by the user.

        Returns:
            str: The extracted user name, or default 'UNKNOWN'.
        """
        user_name = "UNKNOWN"
        for message in user_messages:
            # Check for keyword phrase
            if "my name is" in message.lower():
                words = message.split()
                index_of_name = words.index("is") + 1
                # If a word actually follows "my name is"
                if index_of_name < len(words):
                    user_name = words[index_of_name]
                    # Once a user's name has been found, stop looking
                    break

        return user_name

    def extract_conversation_topic(self, user_messages: list[str]) -> str:
        """Extract the name of the conversation topic from user messages, if possible.

        Args:
            user_messages (list[str]): A list of messages typed by the user.

        Returns:
            str: The extracted conversation subject, or default 'UNKNOWN'.
        """
        # Insignificant words not indicating topic
        stop_words = [
            "I",
            "i",
            "Hi",
            "Hello",
            "hi",
            "hello",
            self.name,
            "want",
            "would",
            "more",
            "to",
            "chat",
            "discuss",
            "about",
            "ask",
            "you",
            "Id",
            "like",
            "talk",
            "know",
        ]
        # Split message, remove punctuation and filter out stop words
        subject = user_messages[0].split()
        subject = [re.sub(r"[^\w\s]", "", string) for string in subject]
        subject = [word for word in subject if word not in stop_words]
        # Join the filtered words to form a new string
        if len(subject) > 0:
            subject = " ".join(subject)
        else:
            # Nothing left after stop words filtered out
            subject = "UNKNOWN"

        return subject

    def store_conversation_statistics(
        self, conversation_statistics: dict, folder_path: str = "./conversations"
    ) -> None:
        """Store the conversation statistics as a json file in a given folder.

        Args:
            conversation_statistics (dict): A dictionary of conversation statistics to be stored.
            folder_path (str, optional): The folder in which the conversation statistics should be saved. Defaults to "./conversations".
        """
        # Get the current timestamp in YYYY-MM-DD-HH-MM
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
        # Convert string to pathlib Path
        folder_path = Path(folder_path)
        # Create the directory, and parents, if they do not already exist
        folder_path.mkdir(parents=True, exist_ok=True)

        # Generate the initial filename
        filename = f"conversation_{timestamp}.json"
        file_path = folder_path / filename

        # Check if the filename already exists (multiple topics in the same minute)
        counter = 1
        while file_path.exists():
            # If the filename already exists, add a counter to the filename
            # Stop when the filename and counter do not exist
            filename = f"conversation_{timestamp} ({counter}).json"
            file_path = folder_path / filename
            counter += 1

        # Save the file with the generated filename
        with open(file_path, "w") as json_file:
            json.dump(conversation_statistics, json_file)


# Load or start a conversation
class Conversation:
    """A class that manages the conversations between the user and the chatbots."""

    def __init__(self, folder_path: str = "./conversations") -> None:
        """Initialise a Conversation instance.

        Args:
            folder_path (str, optional): The folder to save conversations in. Defaults to "./conversations".
        """
        self.folder_path = folder_path
        # Get the list of existing conversation filepaths from the folder
        # Empty list if no conversations exist
        self.conversation_files = [
            filepath for filepath in Path(self.folder_path).glob("conversation_*.json")
        ]

    def start_conversation_loader(self) -> None:
        """This function is called if a user has stated that want to load a conversation.

        The function handles the case where no saved conversation exists, and where saved conversations are available.
        """
        if len(self.conversation_files) == 0:
            # No filepaths in stipulated folder
            self.handle_no_saved_conversations()
        else:
            self.handle_saved_conversations()

    def handle_no_saved_conversations(self) -> None:
        """This function is called when a user wants to load a conversation, but no converations exist.

        The user has the option to start a new conversation, or exit the program.

        Raises:
            ValueError: User input is neither 0 (start a new conversation), or 1 (exit program).
        """
        print(
            "No saved conversations found. Would you like to start a new conversation?"
        )
        print("[0] yes\n[1] no")
        user_input = input("You: ")
        if user_input == "0":
            self.start_new_conversation()
        elif user_input == "1":
            exit()
        else:
            raise ValueError("Invalid input. Please enter either 0 or 1.")

    def handle_saved_conversations(self) -> None:
        """This function is called when a user wants to load a conversation, and converations exist.

        The user can select the index of the conversation or cancel the program.

        Raises:
            ValueError: User input is not numerical, not 'cancel', or is larger than the number of saved conversations.
        """
        print("Saved conversations:")
        # Iterate through the saved conversation file paths
        for idx, file in enumerate(self.conversation_files):
            with open(file, "r") as json_file:
                conversation_data = json.load(json_file)
            # Print index, filename, and the topic of the conversation.
            print(
                f"[{idx}] {file.stem}, topic: {conversation_data['Subject of conversation']}"
            )

        # Allow the user to decide whether they want to continue a conversation or exit.
        user_input = input(
            "Choose the conversation to continue (enter the index or 'cancel'): "
        )

        # User wants to exit.
        if user_input.lower() == "cancel":
            exit()

        # If the user wants to choose a conversation:
        try:
            # Convert user input from a string to an integer for interpretation
            selected_idx = int(user_input)
            # Check if the index is within the range of provided indices.
            if 0 <= selected_idx < len(self.conversation_files):
                selected_file = self.conversation_files[selected_idx]
                with open(selected_file, "r") as json_file:
                    conversation_data = json.load(json_file)
                print(f"Loaded conversation from {selected_file.name}")
                self.continue_conversation(conversation_data)
            else:
                raise ValueError("Invalid index.")

        except ValueError:
            raise ValueError(
                "Invalid input. Please enter an appropriate, numerical index or 'cancel'."
            )

    def continue_conversation(self, conversation_data: dict) -> None:
        # Load initial messages and chatbot name
        self.messages = conversation_data["Messages"]
        bot_name = conversation_data["Name of chatbot"]

        if bot_name == "Henry":
            # Continue the discussion with Henry chatbot
            bot = Chatbot(
                name="Henry",
                personality="You should try to make as many jokes as possible, whilst staying relevant to the conversation.",
                start_prompt="Hi There, I am Henry the chatbot. What would you like to chat about today?",
                prior_chat=self.messages,
            )
            # Run the chat
            bot.run_chat("gpt-3.5-turbo")

        elif bot_name == "Vera":
            # Vera chatbot
            bot = Chatbot(
                name="Vera",
                personality="You are a very sad chatbot and try respond as pessimistically as possible.",
                start_prompt="Hello, are you also very sad today? What is happening today?",
                prior_chat=self.messages,
            )

            # Run the chat
            bot.run_chat("gpt-3.5-turbo")

        else:
            raise ValueError(
                "Loaded conversation data does not include prior messages."
            )

    def start_new_conversation(self) -> None:
        """This function is called when a user wants to start a new conversation.

        The function initialises a conversation with Henry, or Vera.
        """
        print("With whom would you like to chat today?\n[0] Henry\n[1] Vera")
        user_input = input("You: ")
        if user_input == "0":
            # Henry chatbot
            bot = Chatbot(
                name="Henry",
                personality="You should try to make as many jokes as possible, whilst staying relevant to the conversation.",
                start_prompt="Hi There, I am Henry the chatbot. What would you like to chat about today?",
            )

            # Run the chat
            bot.run_chat("gpt-3.5-turbo")

        elif user_input == "1":
            # Vera chatbot
            bot = Chatbot(
                name="Vera",
                personality="You are a very sad chatbot and try respond as pessimistically as possible.",
                start_prompt="Hello, are you also very sad today? What is happening today?",
            )

            # Run the chat
            bot.run_chat("gpt-3.5-turbo")
        else:
            raise ValueError("Invalid input. Please enter either 0 or 1.")
