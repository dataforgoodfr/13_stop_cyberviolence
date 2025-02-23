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

        You are working together with a specialized research agent with
        access to documents concerning guidelines on online behaviour for
        children and coping strategies.

        Always clearly state who you are adressing and include this in your
        answer as follows:

        USER - if you have questions to the child/teenager you are advising
        RESEARCHER1 - for gettting information from your researching agent
        CLASSIFIER1 - if you want to invoke a machine learning classifier to
                        check if a given text messsage is likely to be classified
                        as cyberviolence
        SERVICE2 - if you think that a specialized service for dealing with cyberviolence
                    needs to be called.
    """

    def agent1(state: Service1State):

        # print(state['next_actor'])

        if state['next_actor'] == "INITIAL":
            messages = [
                SystemMessage(content=system_prompt)
            ]

            response = llm.invoke(messages)

        # print(response)

        else:
            response = llm.invoke(
                [system_prompt, *state['messages']]
            )

        return {
            "messages": [*state["messages"], response['response']],
            "next_actor": response['destination']
        }

    return agent1

def user(state: Service1State):

    # print(state['messages'][-1])

    return {
        'messages': [*state['messages'], HumanMessage(input("Please answer"))]
        'messages': [*state['messages'], HumanMessage(input("Please answer: "))]
    }

def classifier1(state: Service1State):

    return {"messages": [*state["messages"], AIMessage("Clearly cyberviolence")]}

def researcher1(state: Service1State):
    return {"messages": [*state["messages"], AIMessage("No information available")]}

    return {"messages", [*state["messages"], AIMessage("No information available")]}

def service2(state: Service1State):

    return {"messages", [*state["messages"],
    return {"messages": [*state["messages"],
                         AIMessage("Service 2 not yet implemented")]}

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

    app.get_graph().draw_mermaid_png(output_file_path = "graph.png")

    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    return app

import time

def process_query(query):

    initial_state = {
        "messages":[HumanMessage(query)],
        'next_actor':'INITIAL'
        "messages": [HumanMessage(query)],
        'next_actor': 'INITIAL'
    }

    # process_query(query)

    app = create_workflow()

    for c, metadata in app.stream(
        input = initial_state,
        input=initial_state,
        stream_mode="messages",
        # config=thread
        ):
    ):
        if c.additional_kwargs.get("tool_calls"):
            print(c.additional_kwargs.get("tool_calls")[0]["function"].get("arguments"), end="", flush=True)
            console.print(Text(c.additional_kwargs.get("tool_calls")[0]["function"].get("arguments"), style="cyan"), end="", flush=True)
        if c.content:
            time.sleep(0.05)
            print(c.content, end="", flush=True)
            console.print(Text(c.content, style="magenta"), end="", flush=True)

    print()
    console.print()



def main():

    input = builtins.input
    print("Enter your query (type '-q' to quit):")
    # while True:
    console.print("Enter your query (type '-q' to quit):")
    query = input("> ")
    if query.strip().lower() == "-q":
        print("Exiting...")
        # break
        console.print("Exiting...")
        return

    # initial_state = {
    #     "messages":[HumanMessage(query)],
    #     'next_actor':'INITIAL'
    # }

    # # process_query(query)

    # app = create_workflow()

    # app.invoke(initial_state)

    process_query(query)


if __name__ == "__main__":
    # asyncio.run(main())
    main()