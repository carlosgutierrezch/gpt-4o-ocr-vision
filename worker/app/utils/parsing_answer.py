# In a new file: worker/app/utils/parser.py

import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import TypeVar, Type, Dict, Any
from worker.app.utils.custom_logs import set_logging

T = TypeVar('T', bound=BaseModel)

class ResponseParser:
    """Handles parsing and validation of LLM responses"""
    
    def __init__(self):
        self.logger = set_logging()
    
    def parse_json_response(self, result: str, model_class: Type[T]) -> T:
        """Parse a JSON string into a Pydantic model
        
        Args:
            result: JSON string to parse
            model_class: Pydantic model class to validate against
            
        Returns:
            An instance of the model_class
            
        Raises:
            HTTPException: If parsing or validation fails
        """
        try:
            parsed_dict = json.loads(result)
            self.logger.info("Successfully parsed JSON from string")
            
            if parsed_dict:
                validated_data = model_class.model_validate(parsed_dict)
                self.logger.info(f"Validated data against {model_class.__name__}")
                return validated_data
            elif isinstance(result, dict):
                validated_data = model_class.model_validate(result)
                self.logger.info(f"Validated dictionary data against {model_class.__name__}")
                return validated_data
            else:
                raise ValueError(f"Unexpected result type: {type(result)}")
                
        except Exception as e:
            error_msg = f"Error processing response: {str(e)}, Result type: {type(result)}"
            if isinstance(result, str):
                error_msg += f", Result preview: {result[:200]}"
            self.logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)