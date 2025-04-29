from flask import Blueprint, request, jsonify
from app.services.ocr import extract_text_from_file, ocr_space_url, LANGUAGE_CODES
from app.services.gemini import simplify_and_translate
from app.utils.downloader import download_file_from_url
import os

process_bp = Blueprint('process', __name__)

@process_bp.route('/process-and-simplify', methods=['POST'])
def process_document():
    data = request.get_json()
    file_url = data.get("file_url")
    
    language = data.get("language")
    if language is None:
        language = data.get("langauge", "English")
    
    auto_detect = data.get("auto_detect", False)
    
    if language not in LANGUAGE_CODES and language != "English":
        return jsonify({
            "error": f"Unsupported language: {language}. Supported languages are: {', '.join(LANGUAGE_CODES.keys())}"
        }), 400

    if not file_url:
        return jsonify({"error": "file_url is required"}), 400

    try:
        lower_url = file_url.lower()
        direct_ocr = any(lower_url.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif'])
        
        if direct_ocr:
            if auto_detect:
                file_path = download_file_from_url(file_url)
                extracted_text = extract_text_from_file(file_path, auto_detect=True)
                
                if os.path.exists(file_path):
                    os.remove(file_path)
            else:
                ocr_lang_code = "eng"
                
                extracted_text = ocr_space_url(file_url, ocr_lang_code)
        else:
            file_path = download_file_from_url(file_url)
            
            extracted_text = extract_text_from_file(file_path, auto_detect=auto_detect)
            
            if os.path.exists(file_path):
                os.remove(file_path)
        
        if extracted_text.startswith("ERROR:"):
            return jsonify({
                "error": extracted_text,
                "suggestion": "Make sure the document is properly formatted and contains actual text content."
            }), 422
        
        if len(extracted_text.strip()) < 10:
            return jsonify({
                "error": "The OCR process produced too little text. The document may be blank or illegible.",
                "original_text": extracted_text,
                "suggestion": "Try a clearer document or a different file format."
            }), 422
        
        result = simplify_and_translate(extracted_text, language)
        
        if result and result.startswith("Sorry,"):
            return jsonify({
                "error": result,
                "original_text": extracted_text,
                "language": language,
            }), 422
            
        return jsonify({
            "original_text": extracted_text,
            "simplified_text": result,
            "language": language,
        })
        
    except Exception as e:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500
