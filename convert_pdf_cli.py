import os
import argparse
from pdf_to_text import convert_pdf_to_text

def validate_file_paths(pdf_path: str, output_path: str) -> tuple[bool, str]:
    """Validate input and output file paths."""
    # Check if PDF file exists
    if not os.path.exists(pdf_path):
        return False, f"Error: PDF file '{pdf_path}' does not exist."
    
    # Check if PDF file has .pdf extension
    if not pdf_path.lower().endswith('.pdf'):
        return False, f"Error: File '{pdf_path}' is not a PDF file."
    
    # Check if output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        return False, f"Error: Output directory '{output_dir}' does not exist."
    
    # Check if output file has .txt extension
    if not output_path.lower().endswith('.txt'):
        return False, f"Error: Output file must have .txt extension."
    
    return True, ""

def print_progress(progress: float, message: str):
    """Print progress updates."""
    print(f"\r{message} - {progress:.1f}% complete", end="")
    if progress >= 100:
        print()  # New line after completion

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert PDF file to text with OCR support.')
    parser.add_argument('pdf_path', help='Path to the input PDF file')
    parser.add_argument('output_path', help='Path for the output text file')
    parser.add_argument('--lang', default='spa', help='Language for OCR (default: spa)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate file paths
    is_valid, error_message = validate_file_paths(args.pdf_path, args.output_path)
    if not is_valid:
        print(error_message)
        return 1
    
    print(f"Converting '{args.pdf_path}' to '{args.output_path}'...")
    print("This may take a while depending on the PDF size and content...")
    
    try:
        # Perform conversion with progress tracking
        success = convert_pdf_to_text(
            pdf_path=args.pdf_path,
            output_path=args.output_path,
            lang=args.lang,
            progress_callback=print_progress
        )
        
        if success:
            print("\nConversion completed successfully!")
            print(f"Output saved to: {args.output_path}")
            return 0
        else:
            print("\nConversion failed. Please check the error messages above.")
            return 1
            
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())