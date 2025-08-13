# Spanish Tax Form Processing API

## Overview

This project provides an API service for processing and validating Spanish tax forms (Model 130). It extracts data from uploaded tax documents using OCR technology and verifies the extracted information against user-provided data.

The system is built with a modular microservice architecture, separating the web API from the worker service that handles the processing tasks.

## Features

- **Document Processing**: Extract information from Model 130 tax forms using advanced OCR
- **Data Verification**: Validate user-provided data against the extracted document information
- **Modular Architecture**: Clean separation between API and processing logic
- **Template-based Prompting**: Customizable prompts stored as templates
- **Advanced Image Preprocessing**: Optimized image processing for better OCR results

## Architecture

The project is structured into two main components:

1. **Web API (`web_api/`)**: Handles HTTP requests and responses
2. **Worker (`worker/`)**: Processes documents and performs data extraction/verification

### Worker Module Structure

```
worker/
├── app/
│   ├── image/
│   │   ├── image_preprocessing.py
│   ├── models/
│   │   ├── schema_130.py
│   │   ├── schema.py
│   ├── pipeline/
│   │   ├── document_service_130.py
│   ├── prompt/
│   │   ├── templates/
│   │   │   ├── extraction_system_prompt.txt
│   │   │   ├── verification_system_prompt.txt
│   │   │   ├── verification_user_prompt.txt
│   │   ├── prompt_manager.py
│   ├── services/
│   │   ├── llm_manager.py
│   ├── utils/
│   │   ├── custom_logs.py
│   │   ├── parsing_answer.py
│   │   ├── parsing_number.py
```

## Requirements

- Python 3.8+
- FastAPI
- Azure OpenAI API access
- PyMuPDF
- Pillow
- dotenv

## Installation

1. Clone the repository:
   ```bash
   git clone https://esja@dev.azure.com/esja/ex_014/_git/ex_014
   cd ex_014
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment variables file:
   ```bash
   # .main.env
   MODEL_NAME=gpt-4o
   TEMPERATURE=0.0
   SEED=42
   TOP_P=0.5
   MAX_TOKENS=5000
   API_VERSION=2023-05-15
   ENDPOINT=your-azure-endpoint
   API_KEY=your-api-key
   ```

   ```bash
   # .image.env
   DPI=300
   FIGSIZE=(10, 10)
   PREVIEW=False
   OPTIMIZE=True
   FORMAT=PNG
   QUALITY=95
   MAX_SIZE_KB=0
   ```

## Usage

### Running the API

```bash
uvicorn web_api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at http://localhost:8000. Documentation is available at http://localhost:8000/docs.

### API Endpoints

- `POST /verify/model_130`: Verify user-provided data against extracted form data

## Development

### Adding New Tax Form Models

1. Create schema definition in `worker/app/models/`
2. Create prompt templates in `worker/app/prompt/templates/`
3. Create document service in `worker/app/pipeline/`
4. Add endpoints to the web API in `web_api/main.py`


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project uses Azure OpenAI services for OCR and document processing
- Special thanks to the FastAPI community for their excellent framework


