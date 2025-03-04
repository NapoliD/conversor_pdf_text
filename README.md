# PDF to Text Converter

This project provides a complete solution for converting PDF files to text, with OCR (Optical Character Recognition) support to extract text from images and scanned PDFs. The solution includes both a command-line interface and a web interface.

## Features

- Extracts text from digital PDFs
- OCR for scanned PDFs or those containing images
- Multi-language support (default set to Spanish)
- Advanced image preprocessing to improve OCR accuracy
- Web interface with real-time progress tracking
- Command-line interface for scripting use

## Prerequisites

### Tesseract OCR

This solution requires Tesseract OCR installed on your system:

- **Windows**: Download and install from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

Make sure to install the required language packages (by default, the application is set to Spanish).

### Poppler

For PDF to image conversion, you need to install Poppler:

- **Windows**: Download the binaries from [https://github.com/oschwartz10612/poppler-windows/releases/](https://github.com/oschwartz10612/poppler-windows/releases/) and add the `bin` folder to your PATH
- **Linux**: `sudo apt-get install poppler-utils`
- **macOS**: `brew install poppler`

## Installation

1. Clone this repository or download the files.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Interface

To convert a PDF to text using the command line:

```bash
python convert_pdf_cli.py path_to_file.pdf output_file.txt --lang spa
```

Options:
- `--lang`: OCR language (default: 'spa' for Spanish)

### Web Interface

To start the web interface:

1. Navigate to the project's root folder.
2. Run:

```bash
python app.py
```

3. Open your browser and go to `http://localhost:5000`
4. Drag and drop your PDF file or click to select it.
5. Wait for the conversion to complete and download the resulting text file.

## Project Structure

```
pdf_to_text_converter/
├── pdf_to_text.py       # Main conversion module
├── convert_pdf_cli.py   # Command-line interface
├── requirements.txt     # Module dependencies
└── README.md            # This file

app.py                  # Flask web application
templates/              # HTML templates for the web interface
└── index.html          # Main page
uploads/                # Folder for temporary files
```

## Customization

You can adjust various parameters to improve conversion quality:

- **DPI**: Increase the value to improve the quality of extracted images (default: 300)
- **Language**: Change the `lang` parameter to use different OCR languages
- **Preprocessing**: Modify the `preprocess_image` function in `pdf_to_text.py` to adjust image preprocessing

## Troubleshooting

- **Tesseract not found error**: Ensure Tesseract is installed and correctly configured in the `pytesseract.pytesseract.tesseract_cmd` variable in `pdf_to_text.py`
- **Poppler error**: Check that Poppler is installed and accessible in your PATH
- **Low OCR quality**: Try increasing DPI or adjusting preprocessing parameters

## License

This project is available under the MIT license.