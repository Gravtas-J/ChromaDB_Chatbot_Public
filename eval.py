import chromadb
import chromadb
import openai
import yaml
from time import time, sleep
from uuid import uuid4
from dotenv import load_dotenv
import os
import streamlit as st
import glob

load_dotenv()



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

def combine_documents(chat_dir):
    # Create a path for all text files in the specified directory
    path = os.path.join(chat_dir, '*.txt')

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
def summarize_content(content):
    summary = ""  # This will hold the final summary
    content_remaining = content  # This will hold the portion of content that has yet to be summarized
    while len(content_remaining) > 0:
        # Split the content_remaining into a chunk to summarize now and the rest to summarize later
        chunk_to_summarize, content_remaining = (
            content_remaining[:1500], content_remaining[1500:]
        )
        # Prepare the conversation object for the chatbot
        conversation_hypothesis = [
            {'role': 'system', 'content': open_file('summarise.md')},
            {'role': 'user', 'content': chunk_to_summarize}
        ]
        # Call the chatbot to summarize this chunk
        chunk_summary = chatbot(conversation_hypothesis)
        # Append the chunk_summary to the final summary
        summary += chunk_summary + "\n"  # Add a newline to separate summaries of different chunks
    return summary


# Usage
directory = 'chat_logs'
combined_content = combine_documents(directory)

def main():

    st.title("Evaluation GUI")
    st.write("experiment to see if the chat logs can be chunked, summarised then the summary put through an analysis.")
    combine_documents('chat_logs')
    # user_input = st.text_input("You: ", "")
    load_dotenv()
    # instantiate ChromaDB
    persist_directory = "chromadb"
    chroma_client = chroma_client = chromadb.PersistentClient(path="persist_directory")
    collection = chroma_client.get_or_create_collection(name="knowledge_base")


    # instantiate chatbot
    openai.api_key = os.getenv("OPENAI_API_KEY")
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_default.txt')})
    user_messages = list()
    all_messages = list()
    
    st.sidebar.title("Chat Summary")
    if st.sidebar.button('Consolidate Chat'):
        combine_documents(directory)
        st.session_state['chat_log'] = combined_content
        summary = summarize_content(st.session_state.get('chat_log', ''))
        st.sidebar.write(summary)
        
    if st.sidebar.button("analyse"):
    
        analysis = [{'role': 'system', 'content': open_file('analysis.md')}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
        hypothesis_report = chatbot(analysis)

        # Displaying the report
        st.sidebar.write(hypothesis_report)




if __name__ == '__main__':
    main()
