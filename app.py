from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import io
import threading
from conversor_pdf_text.pdf_to_text import convert_pdf_to_text, PDFConverter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store conversion progress
conversion_progress = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def progress_callback(file_id, progress, message):
    """Update progress for a specific file conversion"""
    conversion_progress[file_id] = {
        'progress': progress,
        'message': message
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400
    
    try:
        filename = secure_filename(file.filename)
        file_id = f"{filename}_{threading.get_ident()}"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        txt_path = os.path.join(app.config['UPLOAD_FOLDER'], 'CV.txt')
        
        file.save(pdf_path)
        
        # Initialize progress tracking
        conversion_progress[file_id] = {
            'progress': 0,
            'message': 'Iniciando conversión...'
        }
        
        # Create callback function for this specific conversion
        def file_progress_callback(progress, message):
            progress_callback(file_id, progress, message)
        
        # Convert PDF to text with progress tracking
        success = convert_pdf_to_text(
            pdf_path, 
            txt_path, 
            lang='spa',  # Spanish language for OCR
            progress_callback=file_progress_callback,
            dpi=300  # Higher DPI for better quality
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'File converted successfully',
                'filename': 'CV.txt',
                'file_id': file_id
            })
        else:
            return jsonify({'error': 'Failed to convert file'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up PDF file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

@app.route('/progress/<file_id>')
def get_progress(file_id):
    """Get the current progress of a file conversion"""
    if file_id in conversion_progress:
        return jsonify(conversion_progress[file_id])
    return jsonify({'error': 'File ID not found'}), 404

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Create response with the file directly
        response = send_file(
            file_path,
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
