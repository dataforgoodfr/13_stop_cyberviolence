import chainlit as cl
import base64
from PIL import Image
from io import BytesIO
from agents.service1 import create_app
from langchain_core.messages import HumanMessage
from langchain.schema.runnable.config import RunnableConfig

import os
from langfuse.callback import CallbackHandler

import uuid


def encode_image_to_base64(image_path: str) -> str:
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format=img.format)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str


@cl.on_chat_start
async def setup():
    
    # global config
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    app = create_app()
    cl.user_session.set("app", app)
    
    cb = cl.LangchainCallbackHandler()
    
    model_provider = os.getenv("SERVICE1_PROVIDER")
    
    if not model_provider:
        raise EnvironmentError("SERVICE1_PROVIDER env var must be defined")
    
    print(session_id)
    
    lfcb = CallbackHandler(
        secret_key = os.environ.get(f'LANGFUSE_{model_provider.upper()}_SECRET_KEY', ''),
        public_key = os.environ.get(f'LANGFUSE_{model_provider.upper()}_PUBLIC_KEY', ''),
        host="https://cloud.langfuse.com", # 🇪🇺 EU region
        session_id = session_id
    )
    
    cl.user_session.set("lfcb", lfcb)
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
        'first_advice':False,

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
                        RunnableConfig(callbacks = [lfcb], **config)
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
    lfcb = cl.user_session.get("lfcb")
    
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
    emotion = None
    
    # Stream the graph execution
    # given that we are exclusively working with structured output
    # this part can drop the streaming
    async for chunk in app.astream(
        {"messages": human_msg},
        config = RunnableConfig(callbacks = [lfcb], **config),
        stream_mode="updates"  # Use "values" to get the full state at each step
    ):
        print(chunk)
                
            
        if hasattr(chunk, 'keys'):
            for k in chunk.keys():
                print(k)
                if hasattr(chunk[k], 'keys'):
                    
                    # intercept 'emotion' question and provide choices
                    if 'context_data' in chunk[k].keys():
                        if len(chunk[k]['context_data'].keys()) == 4:
                            emotion = await cl.AskActionMessage(
                                content=chunk[k]['messages'][0].content, #"Comment te sens-tu après avoir reçu ce message?",
                                actions=[
                                    cl.Action(name="J'adore", payload={"value": "j'adore"}, label="😍"),
                                    cl.Action(name="Joyeux", payload={"value": "content"}, label="😊"),
                                    cl.Action(name="MDR", payload={"value": "mdr"}, label="🤣"),
                                    cl.Action(name="Pensif", payload={"value": "pensif"}, label="🤔"),
                                    cl.Action(name="Etonne", payload={"value": "etonne"}, label="😮"),
                                    cl.Action(name="Colere", payload={"value": "en colere"}, label="😡"),
                                    cl.Action(name="Triste", payload={"value": "triste"}, label="😥")
                                ],
                                ).send()
                            break

                    # print answer
                    for kk in chunk[k].keys():
                        if kk == "messages" and not isinstance(chunk[k][kk], HumanMessage):
                            print("author: ", k)
                            # Stream the response field specifically
                            answer = cl.Message("", author=k)
                            await answer.stream_token(chunk[k][kk][0].content)
            
                            await answer.send()
    
    # the user chosen emotion has to be fed back to the graph    
    if emotion:
        aimsg = await app.ainvoke(
            {"messages": HumanMessage(emotion.get("payload").get("value"))},
            config = RunnableConfig(callbacks = [lfcb], **config)
        )
        response = aimsg['messages'][-1]
        answer = cl.Message(content=response.content, author = response.author)

        await answer.send()