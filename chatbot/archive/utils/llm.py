import os
# from mistralai import Mistral
from .content import SYSTEM_PROMPT

def complete_chat(input_user, temperature, max_tokens):

    model = "ministral-3b-latest"
    client = Mistral(api_key='xxx')

    chat_response = client.chat.complete(
        model= model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages = [
            {   
                "role": "system",
                "content": SYSTEM_PROMPT,
                "role": "user",
                "content": f"{input_user}"
            },
        ]
    )
    return chat_response.choices[0].message.content