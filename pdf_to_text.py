import PyPDF2
import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF
import os
from typing import Optional, List, Dict
import cv2
import numpy as np
from pdf2image import convert_from_path, convert_from_bytes

class PDFConverter:
    def __init__(self, pdf_path: str, lang: str = 'spa', progress_callback=None, dpi: int = 300):
        self.pdf_path = pdf_path
        self.lang = lang
        self.progress_callback = progress_callback
        self.dpi = dpi  # Higher DPI for better quality images
        # Initialize tesseract path - update this according to your installation
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results with enhanced text extraction"""
        # Convert PIL Image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Apply advanced image preprocessing pipeline
        # Step 1: Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Step 2: Apply adaptive histogram equalization for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(gray)
        
        # Step 3: Advanced noise reduction
        denoised = cv2.fastNlMeansDenoising(equalized, h=10)
        
        # Step 4: Detect skew and rotate if needed
        # Find all contours
        contours, hierarchy = cv2.findContours(denoised, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # Find largest contour - assume it's the text block
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            # Get rotated rectangle
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[2]
            # Correct angle for rotation
            if angle < -45:
                angle = 90 + angle
            # Only rotate if angle is significant
            if abs(angle) > 0.5:
                (h, w) = denoised.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                denoised = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # Step 5: Apply adaptive thresholding for better text extraction
        # Try both global and adaptive thresholding and choose the best one
        global_thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        adaptive_thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Combine both thresholding methods
        combined_thresh = cv2.bitwise_or(global_thresh, adaptive_thresh)
        
        # Step 6: Morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        morph_cleaned = cv2.morphologyEx(combined_thresh, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to PIL Image
        return Image.fromarray(morph_cleaned)

    def update_progress(self, current: int, total: int, message: str = ""):
        """Update progress if callback is provided"""
        if self.progress_callback:
            progress = (current / total) * 100
            self.progress_callback(progress, message)

    def extract_text_from_scanned_pdf(self) -> str:
        """Extract text from scanned PDFs using pdf2image and OCR"""
        complete_text = []
        
        try:
            # Convert PDF to images
            images = convert_from_path(self.pdf_path, dpi=self.dpi)
            total_pages = len(images)
            
            for page_num, image in enumerate(images):
                try:
                    self.update_progress(page_num + 1, total_pages,
                                       f"Processing scanned page {page_num + 1}/{total_pages}")
                    
                    # Preprocess image
                    processed_image = self.preprocess_image(image)
                    
                    # Perform OCR with language support
                    page_text = pytesseract.image_to_string(processed_image, lang=self.lang)
                    
                    if page_text.strip():  # Only add if there's text content
                        complete_text.append(f"\n=== Page {page_num + 1} Text ===\n{page_text}")
                        
                except Exception as e:
                    print(f"Error processing scanned page {page_num + 1}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error converting PDF to images: {str(e)}")
            
        return '\n'.join(complete_text)

    def extract_text_and_images(self) -> str:
        """Extract both text and images from PDF, convert everything to text"""
        complete_text = []
        
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                try:
                    page = doc[page_num]
                    
                    # Extract text
                    text = page.get_text()
                    complete_text.append(f"\n=== Page {page_num + 1} Text ===\n{text}")
                    
                    # Extract images
                    image_list = page.get_images()
                    total_images = len(image_list)
                    
                    self.update_progress(page_num + 1, total_pages,
                                       f"Processing page {page_num + 1}/{total_pages}")
                    
                    for img_index, img in enumerate(image_list):
                        try:
                            # Get image data
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            
                            # Convert to PIL Image
                            image = Image.open(io.BytesIO(image_bytes))
                            
                            # Preprocess image
                            processed_image = self.preprocess_image(image)
                            
                            # Perform OCR with language support
                            image_text = pytesseract.image_to_string(processed_image, lang=self.lang)
                            
                            if image_text.strip():  # Only add if there's text content
                                complete_text.append(
                                    f"\n=== Image {img_index + 1} on Page {page_num + 1} Text ===\n{image_text}")
                            
                            self.update_progress(img_index + 1, total_images,
                                               f"Processing image {img_index + 1}/{total_images} on page {page_num + 1}")
                                
                        except Exception as e:
                            print(f"Error processing image {img_index} on page {page_num + 1}: {str(e)}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing page {page_num + 1}: {str(e)}")
                    continue
                    
        except Exception as e:
            raise Exception(f"Error opening PDF file: {str(e)}")
        finally:
            if 'doc' in locals():
                doc.close()
                
        return '\n'.join(complete_text)
    
    def save_to_txt(self, output_path: str) -> bool:
        """Convert PDF to text file"""
        try:
            # First try standard extraction
            text_content = self.extract_text_and_images()
            
            # If minimal text was extracted, try the scanned PDF approach
            if len(text_content.strip()) < 100:  # Arbitrary threshold
                print("Minimal text detected, trying scanned PDF extraction method...")
                scanned_text = self.extract_text_from_scanned_pdf()
                if len(scanned_text.strip()) > len(text_content.strip()):
                    text_content = scanned_text
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
                
            print(f"Successfully converted PDF to text. Output saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error converting PDF to text: {str(e)}")
            return False

def convert_pdf_to_text(pdf_path: str, output_path: str, lang: str = 'spa',
                       progress_callback=None, dpi: int = 300) -> bool:
    """Utility function to convert PDF to text with progress tracking"""
    converter = PDFConverter(pdf_path, lang, progress_callback, dpi)
    return converter.save_to_txt(output_path)

if __name__ == '__main__':
    # Example usage with progress tracking
    def print_progress(progress: float, message: str):
        print(f"{message} - {progress:.2f}% complete")
    
    pdf_path = 'example.pdf'  # Replace with your PDF path
    output_path = 'output.txt'  # Replace with desired output path
    
    success = convert_pdf_to_text(pdf_path, output_path, progress_callback=print_progress)
    if success:
        print("Conversion completed successfully!")
    else:
        print("Conversion failed. Check the error messages above.")