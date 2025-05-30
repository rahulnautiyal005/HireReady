import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import json
from utils.pdf_parser import extract_text_from_pdf
from utils.string_matching import analyze_resume_text
from utils.pdf_generator import create_pdf_from_text

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-secret")

# Configure logging
logger = logging.getLogger(__name__)

# Configure upload settings
ALLOWED_EXTENSIONS = {'pdf'}
TEMP_FOLDER = tempfile.gettempdir()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['resume']
    
    if not file or file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    if not allowed_file(file.filename):
        flash('Only PDF files are allowed', 'danger')
        return redirect(request.url)
    
    try:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(TEMP_FOLDER, filename)
        file.save(temp_path)
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(temp_path)
        
        if not resume_text or resume_text.strip() == "":
            flash('Could not extract text from the uploaded PDF', 'danger')
            return redirect(request.url)
        
        # Analyze the resume text
        result = analyze_resume_text(resume_text)
        
        # Clean up the temporary file
        os.remove(temp_path)
        
        # Render the results page
        return render_template(
            'results.html', 
            original_text=resume_text,
            improved_text=result['improved_text'],
            improvements=result['improvements'],
            original_filename=filename
        )
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        flash(f'Error processing file: {str(e)}', 'danger')
        return redirect(request.url)

@app.route('/download-improved', methods=['POST'])
def download_improved():
    try:
        improved_text = request.form.get('improved_text', '')
        original_filename = request.form.get('original_filename', 'resume')
        file_base_name = original_filename.rsplit('.', 1)[0]
        
        # Create a temporary file for the improved PDF
        temp_file = os.path.join(TEMP_FOLDER, f"improved_{file_base_name}.pdf")
        
        # Generate PDF from the improved text
        create_pdf_from_text(improved_text, temp_file)
        
        return send_file(
            temp_file,
            as_attachment=True,
            download_name=f"improved_{file_base_name}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error generating improved PDF: {str(e)}")
        flash(f'Error generating improved PDF: {str(e)}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
