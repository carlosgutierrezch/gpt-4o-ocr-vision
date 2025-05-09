import os
from typing import Any
import json
from worker.app.models.schema import (ModelParams,
                               MessageRole,
                               ResponseFormat,
                               InvocationParams)
from worker.app.utils.parsing_number import parse_float,parse_int
from worker.app.utils.custom_logs import set_logging
from openai import AzureOpenAI
from openai import AsyncAzureOpenAI  # Added AsyncAzureOpenAI import
from dotenv import load_dotenv

load_dotenv(".main.env")

class LLM:
    
    def __init__(
        self,
        model_name : str = None,
        temperature : float = None,
        seed: int = None,
        top_p: float = None,
        max_tokens: int = None,
        api_version: str = None,
        azure_endpoint: str = None,
        api_key: str = None,
        **kwargs
    ):

        try:
            
            self.logger = set_logging()
            self.logger.info(f"Initializing the LLM")
            self.model_name = model_name or os.getenv('MODEL_NAME')
            self.temperature = temperature or os.getenv('TEMPERATURE')
            self.seed = parse_int(seed or os.getenv('SEED','42'))
            self.top_p = parse_float(top_p or os.getenv('TOP_P','0.5'))
            self.max_tokens = parse_int(max_tokens or os.getenv('MAX_TOKENS','5000'))
            self.api_version =  api_version or os.getenv('API_VERSION')
            self.azure_endpoint = azure_endpoint or os.getenv('ENDPOINT')
            self.api_key = api_key or os.getenv('API_KEY')
            self.kwargs = kwargs
            self.model_params = ModelParams(
                api_version = self.api_version,
                azure_endpoint = self.azure_endpoint,
                api_key = self.api_key
            )
            self.llm = self._initialize_llm()
            self.async_llm = self._initialize_async_llm()  # Added async client initialization
            self.logger.info("LLm initialized")
        except Exception as e:
            self.logger.info(f"Problem initializing the LLM initialization: {e}")
            raise

    def _initialize_llm(self)->AzureOpenAI:
        model_params_dict = self.model_params.model_dump()
        model_params_dict.update(self.kwargs)
        return AzureOpenAI(**model_params_dict)
    
    def _initialize_async_llm(self)->AsyncAzureOpenAI:  # Added async client initialization method
        model_params_dict = self.model_params.model_dump()
        model_params_dict.update(self.kwargs)
        return AsyncAzureOpenAI(**model_params_dict)
    
    def invoke(self, user_prompt: str, system_prompt:str, response_format_type: json = "json_object")-> json:
        """Synchronous version of invoke (kept for backward compatibility)"""
        messages =[
            {'role':MessageRole.SYSTEM.value,'content':system_prompt},
            {'role':MessageRole.USER.value,'content':user_prompt}
        ]
        
        if response_format_type:
            response_format = ResponseFormat(type=response_format_type)
            
        params = {
            'temperature':self.temperature,
            'seed':self.seed,
            'max_tokens':self.max_tokens,
            'top_p':self.top_p,
            'model':self.model_name,
            'messages':messages
        }
        if response_format:
            params['response_format'] = response_format.model_dump()
        
        params = InvocationParams(**params)
        
        try:
            self.logger.info("Invoking...")
            response = self.llm.chat.completions.create(**params.model_dump(exclude_none=True))
            self.logger.info("Invoke function ran without problems")
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f'Problem with the LLM call :{e}')
    
    async def invoke_async(self, user_prompt: str, system_prompt:str, response_format_type: json = "json_object")-> json:
        """Asynchronous version of invoke"""
        messages =[
            {'role':MessageRole.SYSTEM.value,'content':system_prompt},
            {'role':MessageRole.USER.value,'content':user_prompt}
        ]
        
        if response_format_type:
            response_format = ResponseFormat(type=response_format_type)
            
        params = {
            'temperature':self.temperature,
            'seed':self.seed,
            'max_tokens':self.max_tokens,
            'top_p':self.top_p,
            'model':self.model_name,
            'messages':messages
        }
        if response_format:
            params['response_format'] = response_format.model_dump()
        
        params = InvocationParams(**params)
        
        try:
            self.logger.info("Invoking asynchronously...")
            response = await self.async_llm.chat.completions.create(**params.model_dump(exclude_none=True))
            self.logger.info("Async invoke function ran without problems")
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f'Problem with the async LLM call :{e}')