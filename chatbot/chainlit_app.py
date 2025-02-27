import chainlit as cl
from agents.service1 import create_app
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain.schema.runnable.config import RunnableConfig
import json

config = {"configurable": {"thread_id": 555123412345}}

@cl.on_chat_start
async def setup():
    
    global config
    
    app = create_app()
    cl.user_session.set("app", app)
    
    cb = cl.LangchainCallbackHandler()
    cl.user_session.set("cb", cb)
    cl.user_session.set('config', config)
    
    initial_state = {
        "messages": [
            # SystemMessage(SYSTEM_PROMPT),
            HumanMessage("""
            On va discuter en francais. Presente-toi stp. 
            Après pose la question 'A quel message souhaites-tu répondre ?'
            set action=user_feedback
            """
            )
            ],
        'action': 'user_feedback'
    }
    
    output = app.invoke(initial_state,
                        RunnableConfig(callbacks = [cb], **config)
                        )
    # print(output.content)
    # output = json.loads("".join([*output]))
    content=output['messages'][-1].content
    initial_answer = cl.Message(content)
    
    # for msg, metadata in app.stream(
    #     initial_state,
    #     stream_mode="messages",
    #     config=RunnableConfig(callbacks=[cb],
    #                           **config)):
    #     if (
    #         msg.content
    #         and not isinstance(msg, HumanMessage)
    #         # and metadata["langgraph_node"] == "final"
    #     ):
    #         await initial_answer.stream_token(msg.content)
            
    await initial_answer.send()
    
    
    
    
@cl.on_message
async def on_message(msg: cl.Message):
    
    global config
    
    app = cl.user_session.get('app')
    config = cl.user_session.get("config")
    cb = cl.user_session.get("cb")
    
    
    # for msg, metadata in app.stream(
    #     {"messages": [HumanMessage(content=msg.content)]},
    #     stream_mode="messages",
    #     config=RunnableConfig(callbacks=[cb],
    #                           **config)):
    #     if (
    #         msg.content
    #         and not isinstance(msg, HumanMessage)
    #         and metadata["langgraph_node"] == "final"
    #     ):
    #         await final_answer.stream_token(msg.content)

    output = app.invoke({"messages": [HumanMessage(content=msg.content)]},
                        RunnableConfig(callbacks = [cb], **config)
                        )
    
    # output = json.loads("".join([*output]))
    
    final_answer = cl.Message(content=output['messages'][-1].content)  

    await final_answer.send()
