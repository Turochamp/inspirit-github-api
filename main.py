from openai import OpenAI
import chainlit as cl

client = OpenAI()


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

async def create_streaming_completion(input, response_msg):
    vector_store = retrieve_vector_store()

    stream = client.responses.create(
        model="gpt-4o-mini",
        input=input,
        tools=[{"type": "file_search", "vector_store_ids": [vector_store.id]}],
        temperature=0.1,
        stream=True
    )

    for event in stream:
        if hasattr(event, 'type') and "text.delta" in event.type:
            await response_msg.stream_token(event.delta)

@cl.on_message
async def chat(msg: cl.Message):
    response_msg = cl.Message(content="")
    await response_msg.send()
    
    await create_streaming_completion(msg.content, response_msg)