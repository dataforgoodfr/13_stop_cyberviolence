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
            YOU MUST NOT SPEAK ENGLISH! ONLY FRENCH
            YOU MUST DIRECTLY RETURN action:user_feedback
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
    content = output['messages'][-2].content
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
    
    answer = cl.Message(content="")
    
    # Stream the graph execution
    async for chunk in app.astream(
        {"messages": HumanMessage(msg.content)},
        config = config,
        stream_mode="updates"  # Use "values" to get the full state at each step
    ):
        print(chunk)
        for k in chunk.keys():
            for kk in chunk[k].keys():
                if kk == "messages" and not isinstance(chunk[k][kk], HumanMessage):
                    print("author: ", k)
                    # Stream the response field specifically
                    answer = cl.Message("", author=k)
                    await answer.stream_token(chunk[k][kk][0].content)
            
        await answer.send()
    
    # for msg, metadata in app.stream(
    #     {"messages": [HumanMessage(content=msg.content)]},
    #     stream_mode="messages",
    #     config=RunnableConfig(#callbacks=[cb],
    #                           **config)):
    #     if (
    #         msg.content
    #         and not isinstance(msg, HumanMessage)
    #         # and metadata["langgraph_node"] == "final"
    #     ):
    #         await final_answer.stream_token(msg.content)

    # output = app.invoke({"messages": [HumanMessage(content=msg.content)]},
    #                     RunnableConfig(callbacks = [cb], **config)
    #                     )
    
    # # output = json.loads("".join([*output]))
    
    # for m in output['messages']:
    #     await cl.Message(m.content).send()
    
    # final_answer = cl.Message(content=output['messages'][-1].content)  

    # await final_answer.send()
