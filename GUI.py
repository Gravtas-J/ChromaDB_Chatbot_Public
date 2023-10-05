import chromadb
import openai
import yaml
from time import time, sleep
from uuid import uuid4
from dotenv import load_dotenv
import os
import streamlit as st
import glob



def save_yaml(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

# def combine_documents(chat_dir):
#     # Create a path for all text files in the specified directory
#     path = os.path.join(chat_dir, '*.txt')

#     # Initialize an empty string to hold all the content
#     combined_content = ''

#     # Use glob to get all the text files in the directory
#     for file in glob.glob(path):
#         with open(file, 'r', encoding='utf-8') as f:
#             # Read the content of the current file
#             content = f.read()

#             # Concatenate the content of the current file to the combined_content string
#             combined_content += content + '\n\n'  # Adding two newlines to separate content of different files
        # return combined_content

def combine_documents(directory):
    # Create a path for all text files in the specified directory
    path = os.path.join(directory, '*.txt')

    # Initialize an empty string to hold all the content
    combined_content = ''

    # Use glob to get all the text files in the directory
    for file in glob.glob(path):
        with open(file, 'r', encoding='utf-8') as f:
            # Read the content of the current file
            content = f.read()

            # Concatenate the content of the current file to the combined_content string
            combined_content += content + '\n\n'  # Adding two newlines to separate content of different files

    return combined_content
directory = 'chat_logs'
combined_content = combine_documents(directory)
def chatbot(messages, model="gpt-4", temperature=0):
    max_retry = 7
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)
            text = response['choices'][0]['message']['content']
            
            ###    trim message object
            debug_object = [i['content'] for i in messages]
            debug_object.append(text)
            save_yaml('api_logs/convo_%s.yaml' % time(), debug_object)
            if response['usage']['total_tokens'] >= 7000:
                a = messages.pop(1)
            
            return text
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            if 'maximum context length' in str(oops):
                a = messages.pop(1)
                print('\n\n DEBUG: Trimming oldest message')
                continue
            retry += 1
            if retry >= max_retry:
                print(f"\n\nExiting due to excessive errors in API: {oops}")
                exit(1)
            print(f'\n\nRetrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)

def main():

    st.title("MindTrack Interactive Journal")
    
    user_input = st.text_input("You: ", "")
    load_dotenv()
    # instantiate ChromaDB
    persist_directory = "chromadb"
    chroma_client = chroma_client = chromadb.PersistentClient(path="persist_directory")
    collection = chroma_client.get_or_create_collection(name="knowledge_base")


    # instantiate chatbot
    openai.api_key = os.getenv("OPENAI_API_KEY")
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('System_Prompts\Relfexive_journal.md')})
    user_messages = list()
    all_messages = list()
    
    if user_input:
        # get user input
        text = user_input
        user_messages.append(text)
        all_messages.append('USER: %s' % text)
        conversation.append({'role': 'user', 'content': text})
        save_file('chat_logs/chat_%s_user.txt' % time(), text)
        # st.write(conversation)

        # update main scratchpad
        if len(all_messages) > 5:
            all_messages.pop(0)
        main_scratchpad = '\n\n'.join(all_messages).strip()


        # search KB, update default system
        current_profile = open_file('user_profile.md')
        kb = 'No KB articles yet'
        if collection.count() > 0:
            results = collection.query(query_texts=[main_scratchpad], n_results=1)
            kb = results['documents'][0][0]
            #print('\n\nDEBUG: Found results %s' % results)
        default_system = open_file('System_Prompts\system_default.md').replace('<<PROFILE>>', current_profile).replace('<<KB>>', kb)
        #print('SYSTEM: %s' % default_system)
        conversation[0]['content'] = default_system


        # generate a response
        response = chatbot(conversation)
        save_file('chat_logs/chat_%s_chatbot.txt' % time(), response)
        conversation.append({'role': 'assistant', 'content': response})
        all_messages.append('CHATBOT: %s' % response)
        print('\n\nCHATBOT: %s' % response)
        


        # update user scratchpad
        if len(user_messages) > 3:
            user_messages.pop(0)
        user_scratchpad = '\n'.join(user_messages).strip()


        # update user profile
        print('\n\nUpdating user profile...')
        profile_length = len(current_profile.split(' '))
        profile_conversation = list()
        profile_conversation.append({'role': 'system', 'content': open_file('System_Prompts\system_update_user_profile.md').replace('<<UPD>>', current_profile).replace('<<WORDS>>', str(profile_length))})
        profile_conversation.append({'role': 'user', 'content': user_scratchpad})
        profile = chatbot(profile_conversation)
        save_file('user_profile.md', profile)


        # update main scratchpad
        if len(all_messages) > 5:
            all_messages.pop(0)
        main_scratchpad = '\n\n'.join(all_messages).strip()


        # Update the knowledge base
        print('\n\nUpdating KB...')
        if collection.count() == 0:
            # yay first KB!
            kb_convo = list()
            kb_convo.append({'role': 'system', 'content': open_file('System_Prompts\system_instantiate_new_kb.md')})
            kb_convo.append({'role': 'user', 'content': main_scratchpad})
            article = chatbot(kb_convo)
            new_id = str(uuid4())
            collection.add(documents=[article],ids=[new_id])
            save_file('db_logs/log_%s_add.txt' % time(), 'Added document %s:\n%s' % (new_id, article))
        else:
            results = collection.query(query_texts=[main_scratchpad], n_results=1)
            kb = results['documents'][0][0]
            kb_id = results['ids'][0][0]
            
            # Expand current KB
            kb_convo = list()
            kb_convo.append({'role': 'system', 'content': open_file('System_Prompts\system_update_existing_kb.md').replace('<<KB>>', kb)})
            kb_convo.append({'role': 'user', 'content': main_scratchpad})
            article = chatbot(kb_convo)
            collection.update(ids=[kb_id],documents=[article])
            save_file('db_logs/log_%s_update.txt' % time(), 'Updated document %s:\n%s' % (kb_id, article))
            # TODO - save more info in DB logs, probably as YAML file (original article, new info, final article)
            
            # Split KB if too large
            kb_len = len(article.split(' '))
            if kb_len > 1000:
                kb_convo = list()
                kb_convo.append({'role': 'system', 'content': open_file('System_Prompts\system_split_kb.md')})
                kb_convo.append({'role': 'user', 'content': article})
                articles = chatbot(kb_convo).split('ARTICLE 2:')
                a1 = articles[0].replace('ARTICLE 1:', '').strip()
                a2 = articles[1].strip()
                collection.update(ids=[kb_id],documents=[a1])
                new_id = str(uuid4())
                collection.add(documents=[a2],ids=[new_id])
                save_file('db_logs/log_%s_split.txt' % time(), 'Split document %s, added %s:\n%s\n\n%s' % (kb_id, new_id, a1, a2))
        st.write(response)
    st.sidebar.title("Chat Summary")
    if st.sidebar.button('Consolidate Chat'):
        combine_documents(directory)
        st.sidebar.download_button(
        label="Download Profile",
        data=combined_content,
        file_name=f'chat -.txt',
        mime="text/plain"
        )
if __name__ == '__main__':
    main()
