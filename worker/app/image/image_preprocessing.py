import base64
from io import BytesIO
from PIL import Image
import os
import pymupdf
from fastapi import UploadFile
from typing import List, Tuple, Optional
from worker.app.utils.custom_logs import set_logging
from worker.app.utils.parsing_number import parse_int
from dotenv import load_dotenv

load_dotenv(".image.env")

class ImagePreprocessing:
    """Handles image preprocessing for document analysis"""
    
    def __init__(self):
        """Initialize with configuration from environment variables"""
        self.dpi = parse_int(os.getenv("DPI", "300"))  
        self.figsize = eval(os.getenv("FIGSIZE", "(10, 10)")) 
        self.preview = os.getenv("PREVIEW", "False").lower() == "true"
        self.optimize = os.getenv("OPTIMIZE", "True").lower() == "true"
        self.logger = set_logging()
        self.format = os.getenv("FORMAT", "PNG")
        self.quality = parse_int(os.getenv("QUALITY", "95"))
        self.max_size_kb = parse_int(os.getenv("MAX_SIZE_KB", "0"))  # 0 means no limit
        
    async def process_upload(self, file: UploadFile) -> List[str]:
        """Process an uploaded file and return base64 encoded images
        
        Args:
            file: FastAPI UploadFile object
        
        Returns:
            List of base64 encoded image strings
        """
        self.images = []
        
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # Process based on file type
        if file_extension == ".pdf":
            self._load_pdf_from_bytes(file_content)
        elif file_extension in [".jpg", ".jpeg", ".png"]:
            self._load_image_from_bytes(file_content)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
            
        self.logger.info(f"Loaded {len(self.images)} images from {file.filename}")
        if len(self.images) == 0:
            raise ValueError("No images found in the file.")
            
        base64_results = self.images_to_base64()
        self.logger.info("Processing completed successfully!")
        
        return [url for url, _ in base64_results]
        
    def _load_pdf_from_bytes(self, file_content: bytes):
        """Load images from PDF bytes"""
        try:
            memory_stream = BytesIO(file_content)
            doc = pymupdf.open("pdf", memory_stream)
            for i in range(len(doc)):
                page = doc[i]
                pixmap = page.get_pixmap(dpi=self.dpi)
                image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                self.images.append(image)
        except Exception as e:
            raise Exception(f"Problem loading the PDF file: {e}")

    def _load_image_from_bytes(self, file_content: bytes):
        """Load standard image formats from bytes"""
        try:
            image = Image.open(BytesIO(file_content))

            if hasattr(image, 'info') and 'dpi' in image.info:
                current_dpi = image.info['dpi']
                if current_dpi[0] != self.dpi or current_dpi[1] != self.dpi:
                    width = int(image.width * self.dpi / current_dpi[0])
                    height = int(image.height * self.dpi / current_dpi[1])
                    image = image.resize((width, height), Image.LANCZOS)
            
            self.images.append(image)
        except Exception as e:
            raise Exception(f"Problem loading the image file: {e}")
    
    def images_to_base64(self) -> List[Tuple[str, float]]:
        """Convert all loaded images to base64 encoded strings"""
        results = []
        
        for img in self.images:
            result = self.image_to_base64(
                image=img, 
                format=self.format, 
                quality=self.quality, 
                max_size_kb=self.max_size_kb if self.max_size_kb > 0 else None
            )
            results.append(result)
            
        return results
    
    def image_to_base64(self, image: Image.Image, format: str = "PNG", 
                      quality: int = 95, max_size_kb: Optional[int] = None) -> Tuple[str, float]:
        """Convert an image to base64 encoded string with proper settings for OCR"""
        buffered = BytesIO()
        
        img = image.copy()
        
        if format.upper() == 'JPEG' and img.mode == 'RGBA':
            img = img.convert('RGB')
        
        if format.upper() == 'PNG':
            img.save(buffered, format="PNG", optimize=self.optimize, compress_level=9)
        else:
            img.save(buffered, format="JPEG", quality=quality, optimize=self.optimize)
        
        size_kb = len(buffered.getvalue()) / 1024
        
        if max_size_kb and size_kb > max_size_kb and format.upper() == 'JPEG':
            current_quality = quality
            while size_kb > max_size_kb and current_quality > 90:
                current_quality -= 5
                buffered = BytesIO()
                img.save(buffered, format="JPEG", quality=current_quality, optimize=True)
                size_kb = len(buffered.getvalue()) / 1024
                
            if size_kb > max_size_kb:
                self.logger.warning(f"Image size {size_kb:.2f}KB exceeds limit {max_size_kb}KB, but quality maintained for OCR.")
        
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        base64_data = f"data:image/{format.lower()};base64,{img_str}"
        
        size_bytes = len(base64_data.encode('utf-8'))
        size_kb = size_bytes / 1024
        
        return (base64_data, size_kb)