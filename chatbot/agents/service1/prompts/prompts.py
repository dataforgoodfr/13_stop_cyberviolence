from pathlib import Path

prompt_folder = Path(__file__).parent


with open(prompt_folder / "./agent1_prompt_routage","r") as f:
    agent1_system_prompt = f.read()

with open(prompt_folder / "ask_for_context_system_prompt_fr","r") as f:
    ask_for_context_system_prompt = f.read()

# ask_for_context_system_prompt = agent1_system_prompt + ask_for_context_system_prompt

with open(prompt_folder / "give_advice_system_prompt_fr","r") as f:
    give_advice_system_prompt = f.read()
    
# give_advice_system_prompt = agent1_system_prompt + give_advice_system_prompt

with open(prompt_folder / "research_strategies_system_prompt","r") as f:
    research_strategies_system_prompt = f.read()

with open(prompt_folder / "classify_message_system_prompt","r") as f:
    classify_message_system_prompt = f.read()

with open(prompt_folder / "escalate_system_prompt","r") as f:
    escalate_system_prompt = f.read()