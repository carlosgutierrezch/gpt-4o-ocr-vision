from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from worker.app.models.schema_130 import VerificationResult, TaxFormData, ExtractedFormData
from worker.app.pipeline.document_service_130 import DocumentService
import uuid
from typing import Dict, Optional
from pydantic import BaseModel
from fastapi import UploadFile
import io

verification_results: Dict[str, Optional[VerificationResult]] = {}
processing_status: Dict[str, str] = {}

app = FastAPI(
    title="Solimat Agent gpt-4o",
    description="API for extracting and verifying data",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

def get_document_service():
    return DocumentService()

class JobStatus(BaseModel):
    job_id: str
    status: str

async def process_document(
    job_id: str,
    model_type: str,
    nif: str,
    name: str,
    year: int,
    period: str,
    economic_activities: float,
    agricultural_activities: float,
    self_assessment: float,
    file_content: bytes,
    file_name: str,
    document_service: DocumentService
):
    try:
        processing_status[job_id] = "processing"
        
    
        file = UploadFile(
            file=io.BytesIO(file_content),
            filename=file_name
        )
        
        form_data = TaxFormData(
            Tipo_de_modelo=model_type,
            NIF=nif, 
            Nombre_y_apellidos=name,
            Año=year,
            Periodo=period,
            Casilla_07=economic_activities,
            Casilla_11=agricultural_activities,
            Casilla_19=self_assessment
        )
        
        extracted_data = await document_service.extract_form_data(file)
        
        result = await document_service.verify_form_data(extracted_data, form_data)
        
        verification_results[job_id] = result
        processing_status[job_id] = "completed"
        
    except Exception as e:
        processing_status[job_id] = f"failed: {str(e)}"
        verification_results[job_id] = None

@app.post("/verify/model_130", response_model=JobStatus)
async def verify_form_data_async(
    background_tasks: BackgroundTasks,
    ModelType: str = Form(..., description="Tax form model type"),
    Nif: str = Form(..., description="Tax ID number"),
    Name: str = Form(..., description="Full name"),
    Year: int = Form(..., description="Year"),
    Period: str = Form(..., description="Period"),
    EconomicActivitiesInDirectEstimation: float = Form(..., description="Box 07 amount"),
    AgriculturalActivities: float = Form(..., description="Box 11 amount"),
    SelfAssessmentResult: float = Form(..., description="Box 19 amount"),
    file: UploadFile = File(..., description="Model 130 (PDF,JPEG,JPG)"),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Start asynchronous processing of a tax form verification
    
    Args:
        ModelType: Tax form model type
        Nif: Tax ID number
        Name: Full name
        Year: Year
        Period: Period
        EconomicActivitiesInDirectEstimation: Box 07 amount
        AgriculturalActivities: Box 11 amount
        SelfAssessmentResult: Box 19 amount
        file: The tax form file to process
        
    Returns:
        JobStatus: The job ID and initial status
    """

    job_id = str(uuid.uuid4())
    

    processing_status[job_id] = "queued"
    verification_results[job_id] = None
    
    file_content = await file.read()
    
    background_tasks.add_task(
        process_document,
        job_id,
        ModelType,
        Nif,
        Name,
        Year,
        Period,
        EconomicActivitiesInDirectEstimation,
        AgriculturalActivities,
        SelfAssessmentResult,
        file_content,
        file.filename,
        document_service
    )
    
    return JobStatus(job_id=job_id, status="queued")

@app.get("/verify/model_130/result/{job_id}", response_model=Optional[VerificationResult])
async def get_verification_result(job_id: str):
    """
    Get the result of a completed verification job
    
    Args:
        job_id: The job ID from the async submission
        
    Returns:
        VerificationResult: Results of the verification, or null if not completed
    """
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if processing_status[job_id] != "completed":
        return None
        
    return verification_results[job_id]


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)