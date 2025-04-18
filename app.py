from flask import Flask, request, jsonify, render_template
import os
import PyPDF2
import google.generativeai as genai
import fitz  # PyMuPDF
import re
import subprocess
import tempfile
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get the analysis type from request
    analysis_type = request.form.get('analysis_type', 'question_papers')
    
    # Get the PDF files
    pdf_files = request.files.getlist('pdf_files[]')
    
    pdf_paths = []
    pdf_texts = []
    
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    for pdf in pdf_files:
        pdf_path = os.path.join(upload_dir, pdf.filename)
        pdf.save(pdf_path)
        pdf_paths.append(pdf_path)
        
        # Try multiple extraction methods
        extracted_text = extract_text_with_multiple_methods(pdf_path)
        pdf_texts.append(extracted_text)
    
    genai.configure(api_key=os.getenv('GENAI_API_KEY'))
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
    }
    
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]
    
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                 generation_config=generation_config,
                                 safety_settings=safety_settings)
    
    convo = model.start_chat(history=[])
    
    # Create appropriate prompt based on analysis type
    if analysis_type == 'test_papers':
        prompt = f"these are {len(pdf_texts)} test papers of a student. Do analysis of these test papers and give me 'Key Problems', 'How to Improve'. "
        for i, pdf_text in enumerate(pdf_texts):
            prompt += f"Test paper {i+1}: '{pdf_text}' "
        prompt += ". give the response in html code and in the response don't give any instrucions directly start the Key Problems. don't add the full html boilerplatecode just start from the inner body tags because i want to use the response as the innerHtml of div and don't include the body tag and strictly don't use '*' in the response and i want you to give response without any excuse. put it in a code tag"
    else:  # question_papers
        prompt = f"these are {len(pdf_texts)} question papers. Do analysis and give me 'most frequently asked questions', 'most important questions'. "
        for i, pdf_text in enumerate(pdf_texts):
            prompt += f"question paper {i+1}: '{pdf_text}' "
        prompt += ". give the response in html code and in the response don't give any instrucions directly start the Most Frequently Asked Questions. don't add the full html boilerplatecode just start from the inner body tags because i want to use the response as the innerHtml of div and don't include the body tag and strictly don't use '*' in the response and i want you to give response without any excuse. put it in a code tag"
    
    convo.send_message(prompt)
    result = convo.last.text
    
    # Clean up uploaded files
    for pdf_path in pdf_paths:
        os.remove(pdf_path)
    
    return jsonify({'result': result})

def extract_text_with_multiple_methods(pdf_path):
    """
    Try multiple extraction methods to get text from PDF, 
    starting with simpler methods and escalating to more complex ones if needed.
    """
    # Method 1: Standard PyPDF2
    text = extract_with_pypdf2(pdf_path)
    
    # Check if the extraction yielded meaningful text
    if is_text_meaningful(text):
        return text
    
    # Method 2: PyMuPDF (fitz)
    text = extract_with_pymupdf(pdf_path)
    if is_text_meaningful(text):
        return text
    
    # Method 3: OCR using pdf2image and pytesseract
    text = extract_with_ocr(pdf_path)
    if is_text_meaningful(text):
        return text
    
    # Method 4: Use pdftotext command-line tool if available
    try:
        text = extract_with_pdftotext(pdf_path)
        if is_text_meaningful(text):
            return text
    except:
        pass
    
    # If all methods fail, return whatever we got from the most reliable method
    return text or "Could not extract text from this PDF."

def extract_with_pypdf2(pdf_path):
    """Extract text using PyPDF2."""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            all_text = []
            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(page_text)
                except:
                    continue
            return "\n".join(all_text)
    except Exception as e:
        return f"PyPDF2 extraction error: {str(e)}"

def extract_with_pymupdf(pdf_path):
    """Extract text using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        all_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            all_text.append(page.get_text())
        doc.close()
        return "\n".join(all_text)
    except Exception as e:
        return f"PyMuPDF extraction error: {str(e)}"

def extract_with_ocr(pdf_path):
    """Extract text using OCR via pdf2image and pytesseract."""
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        all_text = []
        for i, image in enumerate(images):
            # Perform OCR on each image
            text = pytesseract.image_to_string(image)
            all_text.append(text)
            
        return "\n".join(all_text)
    except Exception as e:
        return f"OCR extraction error: {str(e)}"

def extract_with_pdftotext(pdf_path):
    """Extract text using the pdftotext command-line tool."""
    try:
        with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
            subprocess.run(['pdftotext', pdf_path, tmp.name], check=True)
            with open(tmp.name, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
    except Exception as e:
        return f"pdftotext extraction error: {str(e)}"

def is_text_meaningful(text):
    """Check if the extracted text is meaningful (not empty or just a few characters)."""
    if not text:
        return False
    
    # Remove whitespace and check if there's substantial content
    cleaned_text = re.sub(r'\s+', '', text)
    return len(cleaned_text) > 100  # Arbitrary threshold

if __name__ == '__main__':
    app.run(debug=True)