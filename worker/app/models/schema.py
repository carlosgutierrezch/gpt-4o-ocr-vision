from typing import Literal, Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class MessageRole(str, Enum):
    SYSTEM='system'
    USER='user'

class ResponseFormat(BaseModel):
    type: Literal['text','json_object'] = 'json_object'

class ModelParams(BaseModel):
    api_version: str
    azure_endpoint: str
    api_key: str

    @field_validator('azure_endpoint')
    def validate_endpoint(cls,v):
        if not v.startswith('https://'):
            raise ValueError('Azure endpoint must start with https://')
        return v

class InvocationParams(BaseModel):
    temperature : float = Field(0.0, ge=0.0, le=1.0)
    seed: int = Field(42, ge=0)
    top_p: float = Field(0.5, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    model: str
    messages: List[Dict[str,Any]]
    response_format : Optional[ResponseFormat] = None
    
    @field_validator('messages')
    def validate_messages(cls,v):
        if not v:
            raise ValueError('Messages can not be empty')
        
        for msg in v:
            if 'role' not in msg or 'content' not in msg:
                raise ValueError(' Each message must have a role and content')
            if msg['role'] not in [role.value for role in MessageRole]:
                raise ValueError(f'Invalid role: {msg["role"]}. Must be one of the {[role.value for role in MessageRole]}')
            return v

class TaxFormData(BaseModel):
    """Input data model for tax form verification"""
    Tipo_de_modelo: str
    NIF: str
    Nombre_y_apellidos: str
    Año: str
    Periodo: str
    Casilla_07: Union[float, int]
    Casilla_11: str
    Casilla_19: Union[float, int]

class ExtractedField(BaseModel):
    """Model for field comparison results"""
    input_value: Any
    document_value: Any
    conclusion: bool
    reasoning: str

class VerificationResult(BaseModel):
    """Model for verification results"""
    Tipo_de_modelo: ExtractedField
    NIF: ExtractedField
    Nombre_y_apellidos: ExtractedField
    Año: ExtractedField
    Periodo: ExtractedField
    Casilla_07: ExtractedField
    Casilla_11: ExtractedField
    Casilla_19: ExtractedField

class ExtractedFormData(BaseModel):
    """Model for OCR extracted data from forms"""
    Chain_of_thought: str
    Tipo_de_modelo: str
    NIF: str
    Nombre_y_apellidos: str
    Año: str
    Periodo: str
    Casilla_01: Optional[str] = None
    Casilla_02: Optional[str] = None
    Casilla_03: Optional[str] = None
    Casilla_04: Optional[str] = None
    Casilla_05: Optional[Any] = None
    Casilla_06: Optional[Any] = None
    Casilla_07: Optional[str] = None
    Casilla_08: Optional[Any] = None
    Casilla_09: Optional[Any] = None
    Casilla_10: Optional[Any] = None
    Casilla_11: Optional[Any] = None
    Casilla_12: Optional[str] = None
    Casilla_13: Optional[Any] = None
    Casilla_14: Optional[str] = None
    Casilla_15: Optional[Any] = None
    Casilla_16: Optional[Any] = None
    Casilla_17: Optional[str] = None
    Casilla_18: Optional[Any] = None
    Casilla_19: Optional[str] = None