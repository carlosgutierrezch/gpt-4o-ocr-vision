import logging
import sys
from typing import List, Tuple, Optional, Union
from pathlib import Path
import os

import pymupdf
from PIL import Image
import matplotlib.pyplot as plt


class ImageProcessor:
    """
    Class for processing and visualizing images from different file formats.
    
    This class allows loading images from PDF files or common image formats,
    processing them and visualizing them according to the specified settings.
    
    Attributes:
        path (Path): Path to the file to process.
        dpi (Optional[int]): Resolution in dots per inch for processing.
        figsize (Tuple[int, int]): Figure size for visualization.
        preview (bool): Indicates whether a preview of the images should be shown.
        logger (logging.Logger): Logger object for recording information.
        images (List[Image.Image]): List of processed images.
    """

    # Supported file extensions
    SUPPORTED_IMAGE_FORMATS = {".jpeg", ".jpg", ".png"}
    SUPPORTED_PDF_FORMAT = ".pdf"
    
    def __init__(self, path: Union[str, Path], dpi: Optional[int], 
                 figsize: Tuple[int, int], preview: bool = False,
                 max_pages: int = 10):
        """
        Initializes a new image processor.
        
        Args:
            path (Union[str, Path]): Path to the file to process.
            dpi (Optional[int], optional): Resolution in DPI. Default 300.
            figsize (Tuple[int, int], optional): Figure size. Default (10, 10).
            preview (bool, optional): Show preview. Default False.
            max_pages (int, optional): Maximum number of pages to process. Default 10.
        
        Raises:
            ValueError: If the file path does not exist.
        """
        self.path = Path(path) if isinstance(path, str) else path
        if not self.path.exists():
            raise ValueError(f"The path '{self.path}' does not exist")
            
        self.dpi = dpi if dpi is not None else 300
        self.figsize = figsize
        self.preview = preview
        self.max_pages = max_pages
        self.logger = self._setup_logging()
        self.images = []
        
        self._validate_file_format()
        
    def _validate_file_format(self) -> None:
        """
        Validates that the file format is supported.
        
        Raises:
            ValueError: If the file format is not supported.
        """
        file_ext = self.path.suffix.lower()
        supported_formats = self.SUPPORTED_IMAGE_FORMATS.union({self.SUPPORTED_PDF_FORMAT})
        
        if file_ext not in supported_formats:
            raise ValueError(
                f"Format '{file_ext}' not supported. Valid formats: {', '.join(supported_formats)}"
            )
    
    def _setup_logging(self) -> logging.Logger:
        """
        Configures and returns a logger object for event logging.
        
        Returns:
            logging.Logger: The configured logger.
        """
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)

    def load_file(self) -> None:
        """
        Loads the specified file and processes it according to its format.
        
        The method automatically detects if the file is a PDF or an image,
        and processes it according to the detected format.
        
        Raises:
            FileNotFoundError: If the file is not found.
            ValueError: If there is a problem processing the file.
            Exception: For other errors during loading.
        """
        self.logger.info(f"Starting file loading: {self.path}")
        
        try:
            file_ext = self.path.suffix.lower()
            
            if file_ext == self.SUPPORTED_PDF_FORMAT:
                self._load_pdf()
            elif file_ext in self.SUPPORTED_IMAGE_FORMATS:
                self._load_image()
            else:
                # This validation was already done in _validate_file_format, but is kept for robustness
                raise ValueError(f"Format '{file_ext}' not supported")
                
        except FileNotFoundError:
            self.logger.error(f"File not found: {self.path}")
            raise
        except ValueError as e:
            self.logger.error(f"Format error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unknown error when loading the file: {e}")
            raise Exception(f"Problem loading the image: {e}")
    
    def _load_pdf(self) -> None:
        """
        Loads a PDF file and extracts its pages as images.
        
        This function processes each page of the PDF up to the established limit
        and converts them into images that are stored in the image list.
        
        Raises:
            ValueError: If there is a problem processing the PDF.
        """
        try:
            document = pymupdf.open(str(self.path))
            page_count = len(document)
            
            self.logger.info(f"Processing PDF with {page_count} pages")
            pages_to_process = min(page_count, self.max_pages)
            
            for i in range(pages_to_process):
                page = document[i]
                pix_map = page.get_pixmap(dpi=self.dpi)
                image = Image.frombytes(
                    "RGB", 
                    [pix_map.width, pix_map.height], 
                    pix_map.samples
                )
                self.images.append(image)
                self.logger.debug(f"Processed page {i+1}/{pages_to_process}")
                
            self.logger.info(f"PDF loaded: {pages_to_process} pages processed")
            
        except Exception as e:
            self.logger.error(f"Error processing the PDF: {e}")
            raise ValueError(f"Could not process the PDF: {e}")
    
    def _load_image(self) -> None:
        """
        Loads an individual image and processes it according to the configuration.
        
        This function loads an image in a common format (.jpg, .jpeg, .png)
        and resizes it according to the specified DPI.
        
        Raises:
            ValueError: If there is a problem processing the image.
        """
        try:
            img = Image.open(self.path)
            original_width, original_height = img.size
            
            # Apply scaling according to DPI
            # Assumes the original image is at 72 DPI (common standard)
            scale_factor = self.dpi / 72.0
            
            if scale_factor != 1:
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                
                self.logger.info(
                    f"Resizing image from {original_width}x{original_height} "
                    f"to {new_width}x{new_height} (DPI: {self.dpi})"
                )
                
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            self.images.append(img)
            self.logger.info("Image successfully loaded")
            
        except FileNotFoundError:
            self.logger.error(f"Image file not found: {self.path}")
            raise
        except Exception as e:
            self.logger.error(f"Error processing the image: {e}")
            raise ValueError(f"Could not process the image: {e}")
    
    def visualize_image(self, image: Image.Image) -> None:
        """
        Visualizes an image using matplotlib.
        
        Args:
            image (Image.Image): Image to visualize.
            
        Raises:
            ValueError: If there is a problem visualizing the image.
        """
        if not isinstance(image, Image.Image):
            raise ValueError("The 'image' parameter must be an instance of PIL.Image.Image")
            
        try:
            plt.figure(figsize=self.figsize)
            plt.imshow(image)
            plt.tight_layout()
            plt.axis("off")
            plt.show()
            self.logger.info("Image visualized")
        except Exception as e:
            self.logger.error(f"Error visualizing the image: {e}")
            raise ValueError(f"Problem visualizing the image: {e}")
    
    def run_pipeline(self) -> List[Image.Image]:
        """
        Executes the complete processing sequence.
        
        This method loads the file, processes the images and optionally
        displays them according to the instance configuration.
        
        Returns:
            List[Image.Image]: List of processed images.
            
        Raises:
            Exception: If there is any error during the process.
        """
        self.logger.info("Starting processing pipeline")
        
        try:
            # Load file
            self.load_file()
            
            # Show preview if enabled
            if self.preview and self.images:
                self.logger.info(f"Showing preview of {len(self.images)} images")
                for i, image in enumerate(self.images):
                    self.logger.info(f"Visualizing image {i+1}/{len(self.images)}")
                    self.visualize_image(image)
            
            self.logger.info("Pipeline completed successfully")
            return self.images
            
        except Exception as e:
            self.logger.error(f"Error in the pipeline: {e}")
            raise Exception(f"Error executing the pipeline: {str(e)}")


if __name__ == "__main__":
    try:
        processor = ImageProcessor(
            path=Path(r"C:\Users\postc\OneDrive\Desktop\ex_014\data\certificado.pdf"),
            dpi=300,
            figsize=(12, 16),
            preview=True,
            max_pages=5
        )
        
        images = processor.run_pipeline()
        print(f"Successfully processed {len(images)} images")
        
    except Exception as e:
        print(f"Error: {e}")