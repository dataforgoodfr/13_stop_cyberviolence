from typing import Annotated, TypedDict, List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

script_folder = Path(__file__).parent

with open(script_folder / "agent1_system_prompt", "r") as f:
    SYSTEM_PROMPT = f.read()

class Service1State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    next_actor: str


class Agent1Response(TypedDict):
    response: Annotated[str, ..., "Response"]
    destination: Annotated[
        Literal['USER', 'RESEARCHER1', 'CLASSIFIER1', 'SERVICE2'], ..., "Recipient of message"
    ]
    # user_input: Annotated[bool, True, "User input required"]

#def create_agent1(llm = ChatOpenAI(model = "gpt-4o-mini", temperature=0)):
#modification due à l'erreur de hust
def  create_agent1(llm=None):
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm = llm.with_structured_output(Agent1Response)

    system_prompt = SYSTEM_PROMPT
    # system_prompt += ""

    def agent1(state: Service1State):
        if state['next_actor'] == "INITIAL":
            messages = [
                SystemMessage(content=system_prompt)
            ]
            response = llm.invoke(messages, config)
        else:
            response = llm.invoke(
                # [SystemMessage(system_prompt), *state['messages']],
                [SystemMessage(system_prompt)] + [*state['messages']],
                config
            )
            
        try:
            # sometimes the return dict has keys = ['type', 'properties']
            # print(response.keys())
            assert 'destination' in response.keys()
        #modification du à l'erreur
        #except:
        except Exception:
            
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
        print(response)    
        AIMessage(response['response']).pretty_print()
        print()
        print('---')
        console.print('[blue] Routed to: ', response['destination'])
        # console.print('[blue] Input needed: ', response['user_input'])
        print('---')
        print()
        
        return {
            "messages": [AIMessage(response['response'])],
            "next_actor": response['destination'],
            # "user_input": response['user_input']
        }

    return agent1

def user(state: Service1State):

    # user_message = HumanMessage(
    #         Prompt.ask("[red]> ")
    #         )
    
    # user_message.pretty_print()
    # print()
    
    return {
        'messages': [*state['messages']]#, user_message]
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
    # workflow.add_edge("USER", "Agent1")
    workflow.add_edge("USER", END)
    workflow.add_edge("SERVICE2", END)

    memory = MemorySaver()

    app = workflow.compile(checkpointer = memory)
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    return app


# async def process_query(query):
#     initial_state = {
#         "messages": [HumanMessage(query)],
#         'next_actor': 'bla'
#     }

#     # app = create_workflow()

#     async for c, metadata in app.astream(
#         input=initial_state,
#         stream_mode="messages",
#     ):
#         if c.additional_kwargs.get("tool_calls"):
#             console.print(Text(c.additional_kwargs.get("tool_calls")[0]["function"].get("arguments"), style="cyan"), end="", flush=True)
#         if c.content:
#             # console.print("\n")
#             time.sleep(0.05)
#             # console.print(Text(c.content, style="magenta"), end="")#, flush=True)

#     console.print("\n")
#     console.print("finally new line")
    
def main():

    global app, config

    initial_state = {
        "messages": [
            # SystemMessage(SYSTEM_PROMPT),
            HumanMessage("""
            On va discuter en francais. Presente-toi stp. 
            Après pose la question 'A quel message souhaites-tu répondre ?'
            """
            )
            ],
        'next_actor': 'Agent1'
    }

    app = create_workflow()

    config = {'configurable':{'thread_id' : "1"}}
    
    app.invoke(initial_state, config)

    # input = builtins.input
    # console.print("Enter your query (type '-q' to quit):")
    # query = input("> ")
    # if query.strip().lower() == "-q":
    #     console.print("Exiting...")
    #     return

    # await process_query(query)

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
    
