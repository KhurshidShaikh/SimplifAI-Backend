import requests
import json
import os
import fitz  
import docx 
import re
import tempfile
from PIL import Image
import string
import pytesseract # type: ignore
from dotenv import load_dotenv

load_dotenv()

OCR_SPACE_API_KEY = os.getenv('OCR_SPACE_API_KEY', 'helloworld')

LANGUAGE_CODES = {
    "English": "eng", 
    "Hindi": "hin",
    "Marathi": "mar",
    "Tamil": "tam",
    "Telugu": "tel",
    "Bengali": "ben",
    "Gujarati": "guj",
    "Kannada": "kan",
    "Malayalam": "mal",
    "Punjabi": "pan",
    "Urdu": "urd"
}

DEFAULT_LANG = "eng"

def detect_script_in_image(image_path):
    try:
        img = Image.open(image_path)
        
        eng_text = pytesseract.image_to_string(img, lang='eng')
        
        english_quality = 0
        if eng_text:
            english_words = [word for word in eng_text.split() if len(word) >= 2]
            english_quality = len(english_words)
        
        if english_quality >= 5:
            return 'english'
        
        hin_text = pytesseract.image_to_string(img, lang='hin')
        devanagari_count_hindi = 0
        total_chars_hindi = 0
        
        for char in hin_text:
            total_chars_hindi += 1
            if '\u0900' <= char <= '\u097F':
                devanagari_count_hindi += 1
        
        mar_text = pytesseract.image_to_string(img, lang='mar')
        devanagari_count_marathi = 0
        total_chars_marathi = 0
        
        for char in mar_text:
            total_chars_marathi += 1
            if '\u0900' <= char <= '\u097F':
                devanagari_count_marathi += 1
                
        hindi_ratio = devanagari_count_hindi / max(total_chars_hindi, 1)
        marathi_ratio = devanagari_count_marathi / max(total_chars_marathi, 1)
        
        if devanagari_count_hindi >= 15 and hindi_ratio > 0.2:
            eng_text2 = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
            eng_words2 = [word for word in eng_text2.split() if len(word) >= 2]
            
            if len(eng_words2) > 10 and devanagari_count_hindi < 20:
                return 'english'
            
            return 'hindi'
            
        if devanagari_count_marathi >= 15 and marathi_ratio > 0.2:
            eng_text2 = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
            eng_words2 = [word for word in eng_text2.split() if len(word) >= 2]
            
            if len(eng_words2) > 10 and devanagari_count_marathi < 20:
                return 'english'
                
            return 'marathi'
        
        return 'english'
    
    except Exception as e:
        print(f"Error in script detection: {str(e)}")
        return 'english'

def extract_text_from_file(file_path, language="English", auto_detect=False):
    try:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):
            language_code = "eng"
            
            if auto_detect:
                detected_script = detect_script_in_image(file_path)
                if detected_script == 'hindi':
                    language_code = "hin"
                elif detected_script == 'marathi':
                    language_code = "mar"
                
            return ocr_space_file(file_path, language_code)
        
        elif file_path.lower().endswith('.pdf'):
            return extract_from_pdf(file_path, auto_detect)
            
        elif file_path.lower().endswith('.docx'):
            return extract_from_word(file_path, auto_detect)
            
        else:
            return f"ERROR: Unsupported file format. Supported formats: PNG, JPG, PDF, DOCX"
    except Exception as e:
        return f"ERROR: Failed to extract text: {str(e)}"

def ocr_space_file(file_path, language_code="eng"):
    try:
        url = 'https://api.ocr.space/parse/image'
        payload = {
            'apikey': OCR_SPACE_API_KEY,
            'language': language_code,
            'isOverlayRequired': False,
            'scale': True,
            'OCREngine': 2,
        }
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files, data=payload)
        
        result = response.json()
        
        if result.get('IsErroredOnProcessing', False):
            error_message = result.get('ErrorMessage', [])
            error_details = result.get('ErrorDetails', [])
            return f"ERROR: OCR processing failed: {error_message} {error_details}"
        
        parsed_results = result.get('ParsedResults', [])
        if not parsed_results:
            return "ERROR: No text found in the image."
        
        extracted_text = ""
        for parsed_result in parsed_results:
            text = parsed_result.get('ParsedText', '')
            if text:
                extracted_text += text + "\n"
        
        return extracted_text.strip()
    except Exception as e:
        return f"ERROR: OCR.space API error: {str(e)}"

def ocr_space_url(image_url, language_code="eng"):
    try:
        url = 'https://api.ocr.space/parse/image'
        payload = {
            'apikey': OCR_SPACE_API_KEY,
            'url': image_url,
            'language': language_code,
            'isOverlayRequired': False,
            'scale': True,
            'OCREngine': 2,
        }
        
        response = requests.post(url, data=payload)
        
        result = response.json()
        
        if result.get('IsErroredOnProcessing', False):
            error_message = result.get('ErrorMessage', [])
            error_details = result.get('ErrorDetails', [])
            return f"ERROR: OCR processing failed: {error_message} {error_details}"
        
        parsed_results = result.get('ParsedResults', [])
        if not parsed_results:
            return "ERROR: No text found in the image."
        
        extracted_text = ""
        for parsed_result in parsed_results:
            text = parsed_result.get('ParsedText', '')
            if text:
                extracted_text += text + "\n"
        
        return extracted_text.strip()
    except Exception as e:
        return f"ERROR: OCR.space API error: {str(e)}"

def extract_from_pdf(pdf_path, auto_detect=False):
    try:
        doc = fitz.open(pdf_path)
        extracted_text = ""
        
        direct_text = ""
        for page in doc:
            page_text = page.get_text()
            if page_text.strip():
                direct_text += page_text + "\n"
        
        if direct_text.strip() and len(direct_text.strip()) > 50:
            return direct_text
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                zoom = 2.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                img_path = os.path.join(temp_dir, f"page_{page_num}.png")
                pix.save(img_path)
                
                page_text = ocr_space_file(img_path, language_code="eng")
                if auto_detect:
                    detected_script = detect_script_in_image(img_path)
                    if detected_script == 'hindi':
                        page_text = ocr_space_file(img_path, language_code="hin")
                    elif detected_script == 'marathi':
                        page_text = ocr_space_file(img_path, language_code="mar")
                
                if not page_text.startswith("ERROR:"):
                    extracted_text += page_text + "\n\n"
            
            if not extracted_text.strip():
                return "ERROR: Could not extract readable text from this PDF."
            
            return extracted_text
    except Exception as e:
        return f"ERROR: Failed to extract text from PDF: {str(e)}"

def extract_from_word(docx_path, auto_detect=False):
    try:
        doc = docx.Document(docx_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            para_text = paragraph.text
            if para_text.strip():
                text += para_text + "\n"
        
        if text.strip() and len(text.strip()) > 20:
            return text
        
        try:
            import win32com.client
            import pythoncom
            
            pythoncom.CoInitialize()
            
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            
            pdf_path = docx_path.replace(".docx", ".pdf")
            doc = word.Documents.Open(docx_path)
            doc.SaveAs(pdf_path, FileFormat=17)
            doc.Close()
            word.Quit()
            
            if os.path.exists(pdf_path):
                pdf_text = extract_from_pdf(pdf_path, auto_detect)
                
                os.remove(pdf_path)
                
                if pdf_text.strip():
                    return pdf_text
        except Exception as pdf_convert_err:
            print(f"Failed to convert Word to PDF: {pdf_convert_err}")
        
        return text
    except Exception as e:
        return f"ERROR: Failed to extract text from Word document: {str(e)}"
