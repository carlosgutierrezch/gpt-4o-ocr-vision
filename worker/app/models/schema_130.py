from typing import Any, Union, Optional
from pydantic import BaseModel,field_validator,Field

class TaxFormData(BaseModel):
    """Input data model for tax form verification"""
    Tipo_de_modelo: str
    NIF: str
    Nombre_y_apellidos: str
    Año: int
    Periodo: str
    Casilla_07: Union[float, int]
    Casilla_11: Union[float, int]
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
    Casilla_05: Optional[str] = None
    Casilla_06: Optional[str] = None
    Casilla_07: Optional[str] = None
    Casilla_08: Optional[str] = None
    Casilla_09: Optional[str] = None
    Casilla_10: Optional[str] = None
    Casilla_11: Optional[str] = None
    Casilla_12: Optional[str] = None
    Casilla_13: Optional[str] = None
    Casilla_14: Optional[str] = None
    Casilla_15: Optional[str] = None
    Casilla_16: Optional[str] = None
    Casilla_17: Optional[str] = None
    Casilla_18: Optional[str] = None
    Casilla_19: Optional[str] = None
    
    
    # Validator to convert Spanish formatted numbers to Python numbers
    @field_validator('Casilla_01', 'Casilla_02', 'Casilla_03', 'Casilla_04', 'Casilla_05', 'Casilla_06', 'Casilla_08', 
               'Casilla_09', 'Casilla_10', 'Casilla_12', 'Casilla_13', 'Casilla_14', 'Casilla_15', 'Casilla_16', 
               'Casilla_17', 'Casilla_18', 'Casilla_19')
    
    def parse_number(cls, value):
        if value is None or value == "null":
            return None
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            # Remove thousands separator and replace decimal comma with point
            cleaned = value.replace(".", "").replace(",", ".")
            try:
                return float(cleaned)
            except ValueError:
                return None
        return value