import chainlit as cl
import base64
from PIL import Image
from io import BytesIO
from agents.service1 import create_app
from langchain_core.messages import HumanMessage, AIMessage
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
    # session_id will be used for langgraph and langgfuse
    session_id = str(uuid.uuid4())
    
    # langgraph thread_id for memory
    config = {"configurable": {"thread_id": session_id}}
    
    # save also for chainlit to link feedback to llm experience
    cl.user_session.set("langfuse_session", session_id)
     
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
            HumanMessage("")
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

# DATA LAYER SETUP
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.data.storage_clients.gcs import GCSStorageClient

gcs_creds = {
    k:os.environ[f"GOOGLE_{k.upper()}"] for k in ('project_id', 'client_email', 'private_key', 'bucket_name')
}

gcs_creds['private_key'] = gcs_creds['private_key'].replace('\\n', '\n') 

storage_client = GCSStorageClient(
    **gcs_creds
)

@cl.data_layer
def get_data_layer():
    return SQLAlchemyDataLayer(
        # conninfo="sqlite+aiosqlite:///cl_data_layer/cl_data_layer.db",
        conninfo = os.environ['DL_CONNINFO'].replace("postgres", "postgresql+psycopg"),
        storage_provider=storage_client
    )

from sqlalchemy import text

@cl.action_callback("handle_feedback")
async def handle_feedback_action(action):
    # Extract feedback and comment from the action payload
    value = action.payload.get("feedback")  # value 1-10
    comment = action.payload.get("comment", "")
    thread_id = action.payload.get("thread_id")

    if not thread_id:
        # Try to fetch from context if not in session
        thread_id = getattr(cl.user_session, "id", None)
    if not thread_id:
        await cl.Message(content="Could not determine thread ID for feedback.").send()
        return

    # Generate a new UUID for the feedback entry
    feedback_id = str(uuid.uuid4())

    # Insert feedback into the longfeedbacks table using the Chainlit data layer
    # keep only the most recent feedback for a given thread
    # # sqlite
    # query = text("""
    #     INSERT OR REPLACE INTO longfeedbacks (id, threadId, value, comment)
    #     VALUES (:id, :threadId, :value, :comment)
    #     ON CONFLICT (threadId) DO UPDATE SET
    #     id = excluded.id,
    #     value = excluded.value,
    #     comment = excluded.comment;
    # """)

    # PostgreSQL
    # need to quote camel case column names to keep camel case
    query = text("""
        INSERT INTO longfeedbacks (id, "threadId", value, comment)
        VALUES (:id, :threadId, :value, :comment)
        ON CONFLICT ("threadId") DO UPDATE SET
            id = EXCLUDED.id,
            value = EXCLUDED.value,
            comment = EXCLUDED.comment;
    """)

    # print(cl.datalayer())

    try:
        async with get_data_layer().engine.begin() as conn:
            await conn.execute(query, {
                "id": feedback_id,
                "threadId": thread_id,
                "value": value,
                "comment": comment
            })
        await cl.Message(content="Thank you for your feedback!").send()
    except Exception as e:
        raise e
        await cl.Message(content=f"Failed to save feedback: {e}").send()
    
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
    
    if msg.content.startswith("#feedback"):
        feedback_element = cl.CustomElement(name="FeedbackWidget")
        await cl.Message(content="Please provide your feedback:", elements=[feedback_element]).send()
        return
    
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