# Persistent Chatbot README

## Overview

This Python script integrates ChromaDB, OpenAI's GPT-4 model, and various utility functions to build a chatbot. The script demonstrates a complete flow of a conversational agent that can update and consult a Knowledge Base (KB), interact with users, and even dynamically update the system and user profiles. 

## Dependencies

- `chromadb`
- `openai`
- `yaml`
- `dotenv`
- `os`
- `uuid`
- `time`

## Functions

### `save_yaml(filepath, data)`

Saves data into a YAML file.

### `save_file(filepath, content)`

Saves a string content into a file.

### `open_file(filepath)`

Opens a file and returns its content.

### `chatbot(messages, model="gpt-4", temperature=0)`

Generates a text-based response using OpenAI's GPT-4 model.

### `get_user_input(user_messages, all_messages, conversation)`

Collects user input and updates data structures storing the conversation.

### `update_knowledge_base(collection, main_scratchpad, chatbot, open_file, save_file)`

Updates the knowledge base stored in ChromaDB.

### `update_system_with_kb(collection, main_scratchpad, conversation)`

Updates the system with information from the KB and user profile.

### `update_user_profile(current_profile, user_scratchpad, open_file, save_file, chatbot)`

Updates the user profile by consulting the chatbot.

### `main()`

The main function that coordinates the entire chatbot functionality.

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API Key. Make sure you have it in your `.env` file or set in the environment.

## How to Run

1. Make sure you have all the dependencies installed.
2. Populate the `.env` file with your OpenAI API key.
3. Run `python <script_name>.py` - this can be any version of the chat. 

## Logging

- API conversations are logged in `api_logs` directory.
- Chat logs are stored in `chat_logs`.
- Database logs are saved in `db_logs`.

## Important Notes

- Make sure you have your `.env` file in the same directory as the script or set your OpenAI API key in the environment.
- The default path for ChromaDB is "chromadb", make sure the directory exists or specify a different path.
- if you wish to change the Persona of the chatbot update the defult system in def the update_system_with_kb & main (under comment instantiate chatbot) 

## Future Enhancements

- Implement session management to handle multiple users.
- Add more robust error handling and logging features.
- Include real-time updates and notifications. 

## Known Issues

- Token count limit might be reached if the conversation history becomes too long. The script currently removes the oldest message to handle this, but a more sophisticated approach may be needed.
- Exception handling for API calls is limited to maximum retries.

## License

MIT License
