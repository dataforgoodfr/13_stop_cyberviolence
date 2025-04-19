import os

# import prompts based on model provider

model_provider = os.getenv("SERVICE1_PROVIDER")
if not model_provider:
    raise EnvironmentError("SERIVCE1_PROVIDER env var needs to be defined")

if model_provider == 'gemini':
    from .gemini import *
    
elif model_provider == 'azure':
    from .azure import *