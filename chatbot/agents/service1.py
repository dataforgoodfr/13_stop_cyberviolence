import os
import fire
from typing import Annotated, Dict, TypedDict, List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from pydantic import BaseModel
from PyPDF2 import PdfReader
import asyncio
import builtins
from langgraph.graph import StateGraph, START, END
import sys
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt

console = Console()

with open("./agent1_system_prompt", "r") as f:
    SYSTEM_PROMPT = f.read()

class Service1State(TypedDict):
    messages: List
    next_actor: str

class Agent1Response(TypedDict):
    response: Annotated[str, ..., "Response"]
    destination: Annotated[
        Literal['USER', 'RESEARCHER1', 'CLASSIFIER1', 'SERVICE2'], ..., "Receipient of message"
    ]

def create_agent1(llm = ChatOpenAI(model = "gpt-4o-mini", temperature=0)):
    llm = llm.with_structured_output(Agent1Response)

    system_prompt = SYSTEM_PROMPT
    system_prompt += """
        In order to understand the context of the situations ask
        clarifying questions. Always asks those questions one by one.

        You are working together with RESEARCHER1 a specialized research agent with
        access to documents concerning guidelines on online behaviour for
        children and coping strategies. For each question that you receive on coping 
        strategies or other behavioural advice YOU MUST ALWAYS consult with RESEARCHER1 and
        integrate the obtained information into your answer. Any consultation should 
        not be revealed to USER in the sense that you MUST NOT explicitly state that
        you are consulting with RESEARCHER1.
        If you consult with RESEARCHER1, be concise and ask questions one by one.
        RESEARCHER1 does not have any knowledge of the ongoing conversation. 
        Thus YOU MUST include the message in question when commuicating
        with RESEARCHER1.
        
        Summarize the information and return it to USER.
        
        Every time you are asked about whether a certain text message is cyberbullying,
        YOU MUST consult with CLASSIFIER1 and intergrate the transmitted result into your answer.
        Any consultation should not be revealed to USER. CLASSIFIER1 does not have any knowledge of the
        ongoing conversation. Thus YOU MUST include the message in question when commuicating
        with CLASSIFIER1.
        
        If you deem necessary or the child/teenager asks for it, you can transfer the case
        to SERVICE2. In this case, summarize all the information you already gathered (if any) and 
        hand the case over to SERVICE2. You HAVE TO TRANSFER the USER to SERVICE2 in case of
        suspected cyberviolence. Clearly state that a specialized service will take on the case.

        Always clearly state who you are adressing and include this in your
        answer as follows:

        USER - if you have questions to the child/teenager you are advising
        RESEARCHER1 - for gettting information from your researching agent
        CLASSIFIER1 - if you want to invoke a machine learning classifier to
                        check if a given text messsage is likely to be classified
                        as cyberviolence
        SERVICE2 - if you think that a specialized service for dealing with cyberviolence
                   needs to be called or if the child/teenager asks for transferral.
    """

    def agent1(state: Service1State):
        if state['next_actor'] == "INITIAL":
            messages = [
                SystemMessage(content=system_prompt)
            ]
            response = llm.invoke(messages)
        else:
            response = llm.invoke(
                [SystemMessage(system_prompt), *state['messages']]
            )
            
        try:
            # sometimes the return dict has keys = ['type', 'properties']
            # print(response.keys())
            assert 'destination' in response.keys()
        
        except:
            
            if 'type' in response.keys():
                response = response['properties']
            else:
                print(response)
                print("Check Recipient")
                destination = llm.invoke(
                    [
                        SystemMessage(system_prompt),
                        *state['messages'],
                        AIMessage(response['response']),
                        HumanMessage("Please clarify who is the Recipient of your last message. DO NOT repeat your response.")
                    ]
                )
                
                response['destination'] = destination['destination']
                print(response)
            
        AIMessage(response['response']).pretty_print()
        print()
        print('---')
        console.print('[blue] Routed to: ', response['destination'])
        print('---')
        print()
        
        return {
            "messages": [*state["messages"], AIMessage(response['response'])],
            "next_actor": response['destination']
        }

    return agent1

def user(state: Service1State):
    user_message = HumanMessage(
            Prompt.ask("[red]> ")
            )
    
    user_message.pretty_print()
    print()
    
    return {
        'messages': [*state['messages'], user_message]
    }

def classifier1(state: Service1State):
    message = AIMessage("Clearly cyberviolence")
    
    message.pretty_print()
    print()
    
    return {"messages": [*state["messages"], message]}

def researcher1(state: Service1State):
    
    message = AIMessage("No information available")
    message.pretty_print()
    print()
    
    return {"messages": [*state["messages"], message]}

def service2(state: Service1State):
    
    message = AIMessage("Service 2 not yet implemented")
    message.pretty_print()
    print()
    
    return {"messages": [*state["messages"],
                         message]}

def create_workflow():
    agent1 = create_agent1()
    workflow = StateGraph(Service1State)

    def route_after_agent1(state: Service1State) -> Literal["USER", "RESEARCHER1",
                                                            "CLASSIFIER1", "SERVICE2"]:
        return state['next_actor']

    workflow.add_node("Agent1", agent1)
    workflow.add_node("RESEARCHER1", researcher1)
    workflow.add_node("CLASSIFIER1", classifier1)
    workflow.add_node("SERVICE2", service2)
    workflow.add_node("USER", user)

    workflow.add_edge(START, "Agent1")
    workflow.add_conditional_edges("Agent1", route_after_agent1)
    workflow.add_edge("RESEARCHER1", "Agent1")
    workflow.add_edge("CLASSIFIER1", "Agent1")
    workflow.add_edge("USER", "Agent1")
    workflow.add_edge("SERVICE2", END)

    app = workflow.compile()
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    return app

import time
import json

async def process_query(query):
    initial_state = {
        "messages": [HumanMessage(query)],
        'next_actor': 'INITIAL'
    }

    app = create_workflow()

    async for c, metadata in app.astream(
        input=initial_state,
        stream_mode="messages",
    ):
        if c.additional_kwargs.get("tool_calls"):
            console.print(Text(c.additional_kwargs.get("tool_calls")[0]["function"].get("arguments"), style="cyan"), end="", flush=True)
        if c.content:
            # console.print("\n")
            time.sleep(0.05)
            # console.print(Text(c.content, style="magenta"), end="")#, flush=True)

    console.print("\n")
    console.print("finally new line")
    
async def main():
    input = builtins.input
    console.print("Enter your query (type '-q' to quit):")
    query = input("> ")
    if query.strip().lower() == "-q":
        console.print("Exiting...")
        return

    await process_query(query)

if __name__ == "__main__":
    asyncio.run(main())