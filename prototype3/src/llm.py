import chainlit as cl
from openai import OpenAI

from src.prompt import system_message


client = OpenAI()

messages = [
    {'role': 'system', 'content': system_message}
]

def retrieve_vector_store():
    print("Retreiving vector store...")

    try:
        # List existing vector stores
        vector_stores = client.vector_stores.list()
        existing_store = next((vs for vs in vector_stores.data if vs.name == "dynea_knowledge_base"), None)
        
        if existing_store:
            print(f"Retreiving vector store: {existing_store.name}")
            vector_store = existing_store
        else:
            print("Vector store not found. Please run 01-dynea-vector-store.py first to create it.")
            raise ValueError("Vector store 'dynea_knowledge_base' not found")
    except Exception as e:
        print(f"Error checking vector stores: {e}")
        exit(1)
    

    print(f"Vector store created/retrieved with ID: {vector_store.id}")
    return vector_store

async def answer_question(message: cl.Message, model="gpt-4o-mini", temperature=0.5):
    input_messages = messages.copy()
    input_messages.append(
        {'role': 'user', 'content': message.content}
    )

    message = cl.Message(content="")

    vector_store = retrieve_vector_store()
    stream = client.responses.create(
        model=model,
        input=input_messages,
        tools=[{"type": "file_search", "vector_store_ids": [vector_store.id]}],
        temperature=temperature,
        stream=True
    )

    for event in stream:
        if hasattr(event, 'type') and "text.delta" in event.type:
            await message.stream_token(event.delta)

    messages.append(
        {'role': 'assistant', 'content': message.content}
    )

    await message.update()

