import json
import os
from fastapi import UploadFile
from worker.app.models.schema_130 import ExtractedFormData, TaxFormData
from worker.app.image.image_preprocessing import ImagePreprocessing
from worker.app.utils.custom_logs import set_logging

class PromptManager:
    """Manages the creation of prompts used for data extraction and verification"""
    
    def __init__(self):
        """Initialize the PromptManager instance"""
        self.image_processor = ImagePreprocessing()
        self.logger = set_logging()
        self.templates_path = os.path.join(os.path.dirname(__file__), 'templates')
        
    def _load_template(self, template_name: str) -> str:
        """Load a template file from the templates directory
        
        Args:
            template_name: Name of the template file
            
        Returns:
            The content of the template file as a string
        """
        try:
            file_path = os.path.join(self.templates_path, template_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Error loading template {template_name}: {str(e)}")
            return f"Error loading template: {template_name}"
        
    async def _get_user_prompt(self, file: UploadFile, user:str) -> list:
        """Get the user prompt for extracting data from forms"""    
        base64_images = await self.image_processor.process_upload(file)
        user_prompt = [{
            "type": "text",
            "text": user
        }]
                
        for url in base64_images:
            user_prompt.append({
                "type": "image_url",
                "image_url": {"url": url}
            })
        return user_prompt
        
    def _get_extraction_system_prompt(self) -> str:
        """Get the system prompt for extracting data from forms"""
        return self._load_template('extraction_system_prompt.txt')
        
    def _get_verification_user_prompt(self, extracted_dict: dict) -> str:
        """Get the user prompt for verifying data"""
        template = self._load_template('verification_user_prompt.txt')
        return template.format(extracted_data=json.dumps(extracted_dict))
        
    def _get_verification_system_prompt(self, input_data: TaxFormData) -> str:
        """Get the system prompt for verifying data against input"""
        template = self._load_template('verification_system_prompt.txt')
        return template.format(input_data=input_data.model_dump_json())