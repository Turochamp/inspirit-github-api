import os
import json
import chainlit as cl
from src.llm import answer_question
from typing import Dict, Optional


@cl.set_starters
async def set_starters():
    questions = []
    with open(os.path.join('public', 'questions.json'), 'r') as f:
        questions = json.loads(f.read())
    
    starter_questions = []
    for question in questions:
        starter_questions.append(
                cl.Starter(
                label=question['label'],
                message=question['message']
            ))
    
    return starter_questions


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None
    

@cl.oauth_callback
def oauth_callback(provider_id: str, token: str, raw_user_data: Dict[str, str], default_user: cl.User) -> Optional[cl.User]:
  return default_user


@cl.on_message
async def main(message: cl.Message):
    await answer_question(message)


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")

