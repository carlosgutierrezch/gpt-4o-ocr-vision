import json
from fastapi import UploadFile, HTTPException
from worker.app.models.schema_130 import TaxFormData, ExtractedFormData, VerificationResult,ExtractedField
from worker.app.prompt.prompt_manager import PromptManager
from worker.app.services.llm_manager import LLM
from worker.app.utils.custom_logs import set_logging
from worker.app.utils.parsing_answer import ResponseParser

class DocumentService:
    """Service for document processing and validation"""
    
    def __init__(self):
        """Initialize the service with required components"""
        self.prompt = PromptManager()
        self.llm = LLM()
        self.logger = set_logging()
        self.parser = ResponseParser()
        
    async def extract_form_data(self, file: UploadFile) -> ExtractedFormData:
        """Extract data from a form document"""
        try:
            user_prompt = await self.prompt._get_user_prompt(file,user = "Extrae de manera precisa toda la informacion de estos documentos a los campos correspondientes e imprime los resultados en formato JSON")
            system_prompt = self.prompt._get_extraction_system_prompt()
        
            result = await self.llm.invoke_async(user_prompt, system_prompt)
            self.logger.info(f"LLM result: {result}")

            extracted_data = self.parser.parse_json_response(result, ExtractedFormData)
            return extracted_data
                
        except Exception as e:
            self.logger.error(f"Error in extract_form_data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}") from e
            
    async def verify_form_data(self, extracted_data: ExtractedFormData, input_data: TaxFormData) -> VerificationResult:
        """Verify extracted form data against input data"""
        try:
            extracted_dict = {
                field: getattr(extracted_data, field)
                for field in VerificationResult.__annotations__
                if hasattr(extracted_data, field)
            }
            user_prompt = self.prompt._get_verification_user_prompt(extracted_dict)
            system_prompt = self.prompt._get_verification_system_prompt(input_data)
            
            result = await self.llm.invoke_async(user_prompt, system_prompt)
            self.logger.info(f"Verification result: {result}")
            
            verification_result = self.parser.parse_json_response(result, VerificationResult)
            return verification_result
                
        except Exception as e:
            self.logger.error(f"Error in verify_form_data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error in verification process: {str(e)}")