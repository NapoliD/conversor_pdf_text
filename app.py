from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from pdf_to_text import convert_pdf_to_text
import os

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF'}), 400
    
    try:
        # Save the uploaded PDF
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        
        # Convert PDF to text
        output_filename = os.path.splitext(filename)[0] + '.txt'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        def progress_callback(progress, message):
            print(f"Progress: {progress}%, {message}")
        
        success = convert_pdf_to_text(pdf_path, output_path, progress_callback)
        
        if success:
            return jsonify({
                'success': True,
                'filename': output_filename
            })
        else:
            return jsonify({'error': 'Failed to convert PDF'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True)
