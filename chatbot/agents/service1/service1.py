from typing import Annotated, TypedDict, List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from langchain.schema.runnable.config import RunnableConfig
#modification apporté à cause de la non compilation du pré- commit
#from .prompts import *
from .prompts import (
    agent1_system_prompt, 
    ask_for_context_system_prompt, 
    research_strategies_system_prompt,
    collect_context_system_prompt,
    give_advice_system_prompt
    )
from ..context_collector.required_context_questions import REQUIRED_CONTEXT_QUESTIONS
# sys.path.append("home/kantundpeterpan/projects/dataforgood/13_stopcyberviolence/repo/chatbot")
# print(sys.path)

service1_dir = Path(__file__).parent

with open(service1_dir / "../monster_context/ateliers_jeunes_complete.md", "r") as f:
    research_strategies_system_prompt = research_strategies_system_prompt.format(docs = f.read())

model = 'google/gemini-2.0-flash-001'
# model = 'openai/gpt-4o-mini'
console = Console()

class Service1State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    action: Literal['collect_context', 'ask_for_context', 'give_advice', 'classify_message', 'escalate', 'user_feedback']
    context_complete: bool
    context_data: dict[str, str]
    # the idea here would be not to keep the research reports in the general message flow to 
    # save tokens ... 
    research_result: str
    research_results_ready: bool
    
class Agent1Response(TypedDict):
    # action: Literal['ask_for_context', 'give_advice', 'classify_message', 'escalate']
    action: Literal['ask_for_context', 'give_advice', 'escalate']
    # response: Annotated[str, ..., "Response"]
    
class ResearchResult(TypedDict):
    research_result: Annotated[str, ..., "Answer for the query based on the available documents"]
    action: Literal['give_advice']
    
class ContextQuestion(TypedDict):
    question: Annotated[str, ..., "Question aiming for clarifying the context of the user's inquiry"]

def agent1(state: Service1State, config: RunnableConfig):
    
    # Node setup
    
    llm = ChatOpenAI(model=model, temperature=0)
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
        assert 'action' in response.keys()
    #Modification pour correction pré-commit
    #except:
    except Exception:
        # print(response)    
        if 'type' in response.keys():
            response = response['properties']
    
    message = AIMessage(response['action'])

    message.pretty_print()
    print()
    
    return {
        # 'messages' : [message],
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

def get_next_question(context_data: dict) -> str:
    """Get next question to ask to the user to collect context. If all questions have been asked, return None."""
    if all(question["id"] in context_data.keys() for question in REQUIRED_CONTEXT_QUESTIONS):
        return None

    return REQUIRED_CONTEXT_QUESTIONS[len(context_data.keys())]["question"]

def collect_context(state: Service1State, config: RunnableConfig):
    llm = ChatOpenAI(model=model, temperature=0)
    system_prompt = collect_context_system_prompt
    
    print("next context question (in theory):")
    print(get_next_question(state['context_data']))
    
    if not state["messages"] or (len(state["messages"]) > 0 and state["messages"][-1].type == "human"):
        
        if len(state["messages"]) > 0 and state["messages"][-1].type == "human":
            user_answer = state["messages"][-1].content
            state["context_data"][REQUIRED_CONTEXT_QUESTIONS[len(state["context_data"])]["id"]] = user_answer
            print(state['context_data'])
        
        next_question = get_next_question(state["context_data"])
        
        if next_question is not None:
            system_prompt = system_prompt + "La question a poser: " + next_question
        
        state["context_complete"] = next_question is None

        if state["context_complete"]:
            return {
                "messages": [
                    AIMessage(
                        "Merci pour ces informations. A quel message souhaites-tu répondre ?"
                        )
                    ],
                "context_complete": True,
                "context_data": state["context_data"],
            }
        
        messages = [
            SystemMessage(system_prompt),
            *state['messages']
        ]
        
        response = llm.with_structured_output(ContextQuestion).invoke(messages, config)
        message = AIMessage(response['question'])
        message.pretty_print()
        print()
        
        return {
            'messages': [message],
            "context_complete": False,
            "context_data": state["context_data"]
        }
        
    return state

def should_collect_context(state: Service1State) -> Literal["collect_context", "agent1"]:
    if state["context_complete"]:
        return "agent1"
    else:
        return "collect_context"

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
    
    llm = ChatOpenAI(model=model, temperature=0)
    system_prompt = give_advice_system_prompt
    
    # Check if there is a research request, that has not been consumed yet
    # force give advice to take the research results into account
    # force action=user_feedback
    
    action = None
    
    if state['research_results_ready']:
        
        system_prompt_extension="""Voici les resultats de `research_strategies` que 
        tu dois prendre en compte pour la redaction de ta reponse.
        
        Tu dois les synthetiser et adapter au language de l'utilisateur.
        
        Tu NE DOIT PAS envoyer une 2eme requete a `research_strategies`.
        
        RESEARCH RESULT:
        ================
        """
    
        print('### Got RESEARCH:')
        system_prompt += system_prompt_extension
        # .format(
        #     results = state['research_result'] #state['messages'][-1].content
        # )
        print()
        # print(system_prompt)
        
        #manually set next action
        action = 'user_feedback'
        
    # prepare message flux
    messages = [
        SystemMessage(system_prompt),
        *state['messages'],
    ]
    
    # append the research output if it has not been consumed yet
    if state['research_results_ready']:
        messages.append(
        AIMessage(state['research_result'])
        )
    
    class GiveAdviceAnswer(TypedDict):
        response: Annotated[str, ..., "Response"]
        action: Literal['research_strategies', 'user_feedback']
    
    output = llm.with_structured_output(GiveAdviceAnswer).invoke(messages, config)
    
    try:
        # sometimes the return dict has keys = ['type', 'properties']
        assert 'response' in output.keys()
    #Modification pour correction pre-commit
    #except:
    except Exception:
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
        'action' : output['action'] if not action else action,
        'research_results_ready': False
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
        state['messages'][-1]
    ]
    
    # TODO: do node work
        
    # response = AIMessage("RESEARCH: Not yet implemented")
    
    output = llm.with_structured_output(ResearchResult).invoke(messages, config)
    print(output)
    
    try:
        # sometimes the return dict has keys = ['type', 'properties']
        assert 'research_result' in output.keys()
    #Modification pour correction pre-commit
    #except:
    except Exception:
        # print(response)    
        print(output.keys())
        if 'type' in output.keys():
            output = output['properties']    
    
    ######
    # This is probably not necessary anymore
    if 'RESEARCH:' not in output['research_result']:
        response = AIMessage('RESEARCH: ' + output['research_result'])
    else:
        response = AIMessage(output['research_result'])
    ####
    
    response.pretty_print()
    print()
    
    return {
        # 'messages' : [response],
        'research_result':response.content,
        'research_results_ready':True,
        'action': output['action']
    }


def classify_message(state: Service1State, config: RunnableConfig):
    """
    node code template
    """
    
    # Node setup
    
    #Code retirer car erreur du pre-commit
    
    # TODO: do node work
    
    response = AIMessage("CLASSIFIER: Not yet implemented, DO NOT CALL AGAIN")
    
    return {
        'messages' : [response]
    }


def escalate(state: Service1State, config: RunnableConfig):
    """
    node code template
    """
    
    # Node setup
    
    
    
    # TODO: do node work
    
    response = AIMessage("ESCALATION: Not yet implemented")
    
    return {
        'messages' : [response]
    }

def create_app():
    graph = StateGraph(Service1State)

    graph.add_node("agent1", agent1)
    graph.add_node("collect_context", collect_context)
    graph.add_node("ask_for_context", ask_for_context)
    graph.add_node("give_advice", give_advice)
    graph.add_node("research_strategies", research_strategies)
    graph.add_node("classify_message", classify_message)
    graph.add_node("escalate", escalate)
    graph.add_node("user_feedback", user_feedback)


    graph.add_conditional_edges("__start__", should_collect_context)
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
        'action': 'ask_for_context',
        'context_complete':True,
        'context_data':{
            'role':"recu",
            'platform':'whatsapp',
            'message_type':'prive',
            'emotion':'triste',
            'planned_action':'rien'
        }
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
    
