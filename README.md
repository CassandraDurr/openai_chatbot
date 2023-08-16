# OpenAi Chatbot

This respository provides a chat application that allows users to interact with two chatbots via command line interface. Users can start new conversations, or resume prior conversations.

## Requirements

The only non-standard Python package utilised in this codebase is the OpenAI Python library. The OpenAI Python library requires Python 3.7.1, or later versions. You can setup your environment with:
```
conda create -n "chatbot_env" python=3.10.8 
conda activate chatbot_env
pip install openai
```

## Setup and usage
To use this repository:
1. Clone the repository to your local machine.
2. Navigate to the highest level of the directory where this README is.
3. Create a file called `config.json` and in the json file, paste:
    ```
    {
        "api_key": "insert-gpt-api-key-here"
    }
    ```
    replacing `insert-gpt-api-key-here` with your api key.
4. In terminal, still in the highest directory, execute command `python run.py`.
5. Follow the prompts in terminal.
6. Type `EXIT` in your chat to exit the program.

## Customisation
The personality of the bots, start prompts, exit cues and other settings can be altered in `utils.py`. 