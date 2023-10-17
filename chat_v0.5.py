import chromadb
from chromadb.config import Settings
import openai
import yaml
from time import time, sleep
from uuid import uuid4
import os
from dotenv import load_dotenv
import streamlit as st


Persona = os.path.join('persona', 'Emily_v1.2.md')
Update_user_profile = os.path.join('system_prompts', 'system_update_user_profile.txt')
User = os.path.join('Profiles', 'user_profile.txt')
System_Update_KB = os.path.join('system_prompts', 'system_update_existing_kb.txt')
System_Split_KB = os.path.join('system_prompts', 'system_split_kb.txt')
System_Instantiate_KB = os.path.join('system_prompts', 'system_instantiate_new_kb.txt')




def save_yaml(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

def chatbot(messages, model="gpt-4", temperature=0):
    """
    Function to interact with the OpenAI chatbot model.

    Parameters:
    - messages (list): List of message objects for the chatbot conversation.
    - model (str): OpenAI model to use for generating responses. Default is 'gpt-4'.
    - temperature (float): Controls the randomness of the generated text. Default is 0.

    Returns:
    - text (str): The text generated by the chatbot.
    """
    # Set maximum retries for the API call
    max_retry = 7
    # Initialize retry counter
    retry = 0
    
    while True:
        try:
            # Call OpenAI API to generate chatbot's response
            response = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)
            # Extract the text content from the API response
            text = response['choices'][0]['message']['content']
            
            # Debugging: Save the conversation log for analysis
            debug_object = [i['content'] for i in messages]
            debug_object.append(text)
            save_yaml('api_logs/convo_%s.yaml' % time(), debug_object)
            
            # Check token count, remove oldest message if limit exceeded
            if response['usage']['total_tokens'] >= 7000:
                a = messages.pop(1)
            
            return text
        
        except Exception as oops:
            # Handle exceptions
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            
            # If the exception is due to maximum context length, remove the oldest message
            if 'maximum context length' in str(oops):
                a = messages.pop(1)
                print('\n\n DEBUG: Trimming oldest message')
                continue
            
            # Increment the retry counter
            retry += 1
            
            # Exit if retries exceed the maximum limit
            if retry >= max_retry:
                print(f"\n\nExiting due to excessive errors in API: {oops}")
                exit(1)
            
            # Wait for an exponential backoff time before retrying
            print(f'\n\nRetrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)

def get_user_input(user_messages, all_messages, conversation):
    """
    Get input from the user and update relevant data structures.
    
    Parameters:
    - user_messages (list): A list to store the messages from the user.
    - all_messages (list): A list to store all the messages in the conversation.
    - conversation (list): A list of dictionaries to store the role and content of each message.

    Returns:
    None
    """
    # Get user input
    text = st.text_input('USER:', '')
    
    # Append the user's message to the list of user messages
    user_messages.append(text)
    
    # Append the user's message to the list of all messages
    formatted_text = f'USER: {text}'
    all_messages.append(formatted_text)
    
    # Append the role and content to the conversation list
    conversation.append({'role': 'user', 'content': text})
    
    # Save the user's message to a file
    filename = f'chat_logs/chat_{time()}_user.txt'
    save_file(filename, text)

def update_knowledge_base(collection, main_scratchpad, chatbot, open_file, save_file):
    """
    Update the knowledge base with new or updated articles.
    
    Parameters:
    - collection: The database collection where the KB is stored.
    - main_scratchpad: The content to be added or updated in the KB.
    - chatbot: The function that generates an article for the KB.
    - open_file: Function to open a file and read its content.
    - save_file: Function to save logs.

    Returns:
    - None
    """
    print('\n\nUpdating KB...')
    
    # Check if the KB is empty
    if collection.count() == 0:
        kb_convo = [{'role': 'system', 'content': open_file(System_Instantiate_KB)},  #'system_prompts\\system_instantiate_new_kb.txt'
                    {'role': 'user', 'content': main_scratchpad}]
        article = chatbot(kb_convo)
        new_id = str(uuid4())
        collection.add(documents=[article], ids=[new_id])
        save_file(f'db_logs/log_{time()}_add.txt', f'Added document {new_id}:\n{article}')

    else:
        results = collection.query(query_texts=[main_scratchpad], n_results=1)
        kb = results['documents'][0][0]
        kb_id = results['ids'][0][0]

        kb_convo = [{'role': 'system', 'content': open_file(System_Update_KB).replace('<<KB>>', kb)}, #system_prompts\\system_update_existing_kb.txt
                    {'role': 'user', 'content': main_scratchpad}]
        article = chatbot(kb_convo)
        collection.update(ids=[kb_id], documents=[article])
        save_file(f'db_logs/log_{time()}_update.txt', f'Updated document {kb_id}:\n{article}')

        # Check if the article is too long and needs to be split
        kb_len = len(article.split(' '))
        if kb_len > 1000:
            kb_convo = [{'role': 'system', 'content': open_file(System_Split_KB)}, #system_prompts\\system_split_kb.txt
                        {'role': 'user', 'content': article}]
            articles = chatbot(kb_convo).split('ARTICLE 2:')
            a1 = articles[0].replace('ARTICLE 1:', '').strip()
            a2 = articles[1].strip()
            collection.update(ids=[kb_id], documents=[a1])
            new_id = str(uuid4())
            collection.add(documents=[a2], ids=[new_id])
            save_file(f'db_logs/log_{time()}_split.txt', f'Split document {kb_id}, added {new_id}:\n{a1}\n\n{a2}')

def update_user_profile(current_profile, user_scratchpad, open_file, chatbot, save_file, Update_user_profile, User):
    """
    Update the user profile with new information.
    
    Parameters:
    - current_profile: The current user profile.
    - user_scratchpad: The new information to be added to the user profile.
    - open_file: Function to open a file and read its content.
    - chatbot: The function that generates a response for the user profile update.
    - save_file: Function to save logs.
    - Update_user_profile: The file path of the system prompt for updating the user profile.
    - User: The file path of the user profile.

    Returns:
    - None
    """
    print('\n\nUpdating user profile...')
    profile_length = len(current_profile.split(' '))
    profile_conversation = list()
    profile_conversation.append({'role': 'system', 'content': open_file(Update_user_profile).replace('<<UPD>>', current_profile).replace('<<WORDS>>', str(profile_length))}) #system_prompts\\system_update_user_profile.txt
    profile_conversation.append({'role': 'user', 'content': user_scratchpad})
    profile = chatbot(profile_conversation)
    save_file(User, profile)

def main():
    load_dotenv()
    # instantiate ChromaDB
    persist_directory = "chromadb"
    # chroma_client = chromadb.PersistentClient(Settings(persist_directory=persist_directory,chroma_db_impl="duckdb+parquet",))
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    collection = chroma_client.get_or_create_collection(name="knowledge_base")


    # instantiate chatbot
    openai.api_key = os.getenv("OPENAI_API_KEY")
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file(Persona)}) #Persona\\Emily_v1.2.md
    user_messages = list()
    all_messages = list()

    # get user input
    get_user_input(user_messages, all_messages, conversation)
    if st.button('Submit'):



        # update main scratchpad
        if len(all_messages) > 5:
            all_messages.pop(0)
        main_scratchpad = '\n\n'.join(all_messages).strip()


        # search KB, update default system
        current_profile = open_file(User) #Profiles\\user_profile.txt
        kb = 'No KB articles yet'
        if collection.count() > 0:
            results = collection.query(query_texts=[main_scratchpad], n_results=1)
            kb = results['documents'][0][0]
            #print('\n\nDEBUG: Found results %s' % results)
        default_system = open_file('Persona\\Emily_v1.2.md').replace('<<PROFILE>>', current_profile).replace('<<KB>>', kb)
        #print('SYSTEM: %s' % default_system)
        conversation[0]['content'] = default_system
 

        # generate a response
        response = chatbot(conversation)
        save_file('chat_logs/chat_%s_chatbot.txt' % time(), response)
        conversation.append({'role': 'assistant', 'content': response})
        all_messages.append('CHATBOT: %s' % response)
        st.write('\n\nCHATBOT: %s' % response)


        # update user scratchpad
        if len(user_messages) > 3:
            user_messages.pop(0)
        user_scratchpad = '\n'.join(user_messages).strip()

        update_user_profile(current_profile, user_scratchpad, open_file, chatbot, save_file, Update_user_profile, User)


        # update main scratchpad
        if len(all_messages) > 5:
            all_messages.pop(0)
        main_scratchpad = '\n\n'.join(all_messages).strip()


        # Update the knowledge base
        print('\n\nUpdating KB...')
        update_knowledge_base(collection, main_scratchpad, chatbot, open_file, save_file)


if __name__ == '__main__':
    main()

        
        