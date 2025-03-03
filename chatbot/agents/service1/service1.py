import os
import fire
from typing import Annotated, Dict, TypedDict, List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from PyPDF2 import PdfReader
import asyncio
import builtins
from langgraph.graph import StateGraph, START, END
import sys
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from langchain.schema.runnable.config import RunnableConfig
from .prompts import *
import sys
import os
# sys.path.append("home/kantundpeterpan/projects/dataforgood/13_stopcyberviolence/repo/chatbot")
# print(sys.path)
from ..utils import ChatOpenRouter as ChatOpenAI

model = 'google/gemini-2.0-flash-001'

console = Console()

class Service1State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    action: Literal['ask_for_context', 'give_advice', 'classify_message', 'escalate', 'user_feedback']
    
class Agent1Response(TypedDict):
    response: Annotated[str, ..., "Response"]
    action: Literal['ask_for_context', 'give_advice', 'classify_message', 'escalate']
    
class ContextQuestion(TypedDict):
    question: Annotated[str, ..., "Question aiming for clarifying the context of the user's inquiry"]

def agent1(state: Service1State, config: RunnableConfig):
    
    # Node setup
    
    llm = ChatOpenAI(model=model, temperature=0, stream = True)
    system_prompt = agent1_system_prompt
    messages = [
        SystemMessage(system_prompt),
        *state['messages']
    ]
    
    response = llm.with_structured_output(Agent1Response).invoke(
                # [SystemMessage(system_prompt), *state['messages']],
                messages,
                config
            )
    
    
    try:
        # sometimes the return dict has keys = ['type', 'properties']
        print(response.keys())
        assert 'response' in response.keys()
    
    except:
        # print(response)    
        if 'type' in response.keys():
            response = response['properties']
    
    message = AIMessage(response['response'])

    message.pretty_print()
    print()
    
    return {
        'messages' : [message],
        'action' : response['action']
    }


def router(state: Service1State) -> Literal["ask_for_context","give_advice","classify_message","escalate", "user_feedback"]:
    
    # TODO: routing logic
    
    print()
    print('---')
    console.print('[blue] Routed to: ', state['action'])
    print('---')
    print()

    return state['action']

def user_feedback(state: Service1State, config: RunnableConfig):
    return

def ask_for_context(state: Service1State, config: RunnableConfig):
    
    # Node setup
    
    llm = ChatOpenAI(model=model, temperature=0)
    system_prompt = ask_for_context_system_prompt
    messages = [
        SystemMessage(system_prompt),
        *state['messages']
    ]
    
    # TODO: do node work
    
    response = llm.with_structured_output(ContextQuestion).invoke(messages, config)
    
    message = AIMessage(response['question'])
    message.pretty_print()
    print()
    
    return {
        'messages' : [message]
    }


def give_advice(state: Service1State, config: RunnableConfig):
    
    # Node setup
    
    llm = ChatOpenAI(model=model, temperature=0, stream = True)
    system_prompt = give_advice_system_prompt
    messages = [
        SystemMessage(system_prompt),
        *state['messages']
    ]
    
    class GiveAdviceAnswer(TypedDict):
        response: Annotated[str, ..., "Response"]
        action: Literal['research_strategies', 'user_feedback']
    
    output = llm.with_structured_output(GiveAdviceAnswer).invoke(messages, config)
    
    try:
        # sometimes the return dict has keys = ['type', 'properties']
        assert 'response' in output.keys()
    
    except:
        # print(response)    
        print(output.keys())
        if 'type' in output.keys():
            output = output['properties']
    
    
    print(output)
    response = AIMessage(output['response'])
    print()
    response.pretty_print()
    print()
    
    return {
        'messages' : [response],
        'action' : output['action']
    }
    
def advice_router(state: Service1State) -> Literal["research_strategies", "user_feedback"]:
    
    print()
    print('---')
    console.print('[blue] Routed to: ', state['action'])
    # console.print('[blue] Input needed: ', response['user_input'])
    print('---')
    print()
    
    return state['action']


def research_strategies(state: Service1State, config: RunnableConfig):
    """
    node code template
    """
    
    # Node setup
    
    llm = ChatOpenAI(model=model, temperature=0)
    system_prompt = research_strategies_system_prompt
    messages = [
        SystemMessage(system_prompt),
        *state['messages']
    ]
    
    # TODO: do node work
        
    response = AIMessage("RESEARCH: Not yet implemented")
    
    response.pretty_print()
    print()
    
    return {
        'messages' : [response]
    }


def classify_message(state: Service1State, config: RunnableConfig):
    """
    node code template
    """
    
    # Node setup
    
    llm = ChatOpenAI(model=model, temperature=0)
    system_prompt = classify_message_system_prompt
    messages = [
        SystemMessage(system_prompt),
        *state['messages']
    ]
    
    # TODO: do node work
    
    response = AIMessage("CLASSIFIER: Not yet implemented")
    
    return {
        'messages' : [response]
    }


def escalate(state: Service1State, config: RunnableConfig):
    """
    node code template
    """
    
    # Node setup
    
    llm = ChatOpenAI(model=model, temperature=0)
    system_prompt = escalate_system_prompt
    messages = [
        SystemMessage(system_prompt),
        *state['messages']
    ]
    
    # TODO: do node work
    
    response = AIMessage("ESCALATION: Not yet implemented")
    
    return {
        'messages' : [response]
    }

def create_app():
    graph = StateGraph(Service1State)

    graph.add_node("agent1", agent1)
    graph.add_node("ask_for_context", ask_for_context)
    graph.add_node("give_advice", give_advice)
    graph.add_node("research_strategies", research_strategies)
    graph.add_node("classify_message", classify_message)
    graph.add_node("escalate", escalate)
    graph.add_node("user_feedback", user_feedback)


    graph.add_edge("__start__", "agent1")
    graph.add_conditional_edges("agent1", router)
    # graph.add_edge("give_advice", "research_strategies")
    graph.add_conditional_edges("give_advice", advice_router)
    graph.add_edge("research_strategies", "give_advice")
    graph.add_edge("classify_message", "agent1")
    graph.add_edge("escalate", "__end__")

    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)
    
    return app


# app = create_app()

def main():

    global app, config

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

    app = create_app()
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")

    config = {'configurable':{'thread_id' : "3"}}
    
    app.invoke(initial_state, config)
    
if __name__ == "__main__":
    
    # asyncio.run(main())
    
    main()
    
    print(config)
    
    while True:
        try:
            content = Prompt.ask("[red]> ")
            if content.endswith('-q'):
                break
            user_message = HumanMessage(
                content
            )
            user_message.pretty_print()
            app.invoke({"messages": [user_message]}, config)
            
        except KeyboardInterrupt:
            break
    