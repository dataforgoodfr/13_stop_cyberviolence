import chainlit as cl
import base64
from PIL import Image
from io import BytesIO
from agents.service1 import create_app
from langchain_core.messages import HumanMessage
from langchain.schema.runnable.config import RunnableConfig

config = {"configurable": {"thread_id": 555123412345}}

def encode_image_to_base64(image_path: str) -> str:
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format=img.format)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str


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
            # HumanMessage("""
            # On va discuter en francais. Presente-toi stp. 
            # Après pose la question 'A quel message souhaites-tu répondre ?'
            # YOU MUST NOT SPEAK ENGLISH! ONLY FRENCH
            # YOU MUST DIRECTLY RETURN action:user_feedback
            # """
            # )
            ],
        "context_complete": False,
        "context_data": {},
        'action': 'collect_context',

        # UNCOMMENT TO SKIP intro questions
        # 'action': 'ask_for_context',
        # 'context_complete':False,
        # 'context_data':{
        #     'role':"recu",
        #     'platform':'whatsapp',
        #     'message_type':'prive',
        #     'emotion':'triste',
        #     'planned_action':'rien'
        # },
        
        'research_results_ready':False
    }
    
    output = app.invoke(initial_state,
                        RunnableConfig(callbacks = [cb], **config)
                        )

    content = output['messages'][-1].content
    initial_answer = cl.Message(content)
            
    await initial_answer.send()
    
    
    
    
@cl.on_message
async def on_message(msg: cl.Message):
    
    global config
    
    app = cl.user_session.get('app')
    config = cl.user_session.get("config")
    cb = cl.user_session.get("cb")
    
    # Check for attachements
    if not msg.elements:
        human_msg = HumanMessage(msg.content)
        
    else:
        # Processing images exclusively
        images = [file for file in msg.elements if "image" in file.mime]
        
        # Read the first image
        image_str = encode_image_to_base64(images[0].path)     
    
        human_msg = HumanMessage(
            content=[
                {"type": "text", "text": msg.content},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_str}"},
                },
            ],
        )
        
    answer = cl.Message(content="")
    
    # Stream the graph execution
    async for chunk in app.astream(
        {"messages": human_msg},
        config = RunnableConfig(callbacks = [cb], **config),
        stream_mode="updates"  # Use "values" to get the full state at each step
    ):
        print(chunk)
        if hasattr(chunk, 'keys'):
            for k in chunk.keys():
                if hasattr(chunk[k], 'keys'):
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
