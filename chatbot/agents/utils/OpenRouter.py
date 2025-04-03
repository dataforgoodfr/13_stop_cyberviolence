import os
from langchain_openai import ChatOpenAI
#from typing import *
#Modification pour correction erreur pre-commit
from typing import Optional

class ChatOpenRouter(ChatOpenAI):
    
    """Derived class to be able to use the OpenRouter API
    https://medium.com/@gal.peretz/openrouter-langchain-leverage-opensource-models-without-the-ops-hassle-9ffbf0016da7
    """
    
    def __init__(self,
                 model: str,
                 openai_api_key: Optional[str] = None,
                 openai_api_base: str = "https://openrouter.ai/api/v1",
                 **kwargs):
        openai_api_key = openai_api_key or os.getenv('OPENROUTER_API_KEY')
        super().__init__(openai_api_base=openai_api_base,
                         openai_api_key=openai_api_key,
                         model=model, **kwargs)
    
