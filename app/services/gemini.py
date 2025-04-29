from google import genai
import os
import sys
from pathlib import Path

def load_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        try:
            current_dir = Path(__file__).resolve().parent.parent.parent
            env_path = current_dir / '.env'
            
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.strip() and '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == "GEMINI_API_KEY":
                                api_key = value
                                break
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    return api_key

API_KEY = load_api_key()

try:
    if not API_KEY:
        raise ValueError("API Key not found. Please set the GEMINI_API_KEY environment variable or add it to the .env file.")

    client = genai.Client(api_key=API_KEY)
    
except ValueError as e:
    print(f"Error: {e}")
    print("Please make sure you have set the GEMINI_API_KEY environment variable or added it to the .env file.")
    sys.exit(1)
except Exception as e:
    print(f"Error initializing Google GenAI client: {e}")
    sys.exit(1)

def simplify_and_translate(text_to_process: str, target_language: str):
    if not text_to_process:
        print("Input text is empty. Cannot process.")
        return "Sorry, I couldn't process your request because the extracted text is empty."

    if "unintelligible" in text_to_process.lower() or "gibberish" in text_to_process.lower():
        return "Sorry, the OCR couldn't properly recognize the text in your image. This often happens with non-English text like Hindi or Marathi. Try a clearer image or different file format."
        
    if "unintelligible" in text_to_process.lower() or "simplification is impossible" in text_to_process.lower():
        return "Sorry, the OCR couldn't properly recognize the text in your image. This often happens with non-English text like Hindi or Marathi. Try a clearer image or different file format."

    simplify_prompt = f"""Simplify the following text. The text might be in {target_language} or English, so handle both appropriately. 
    If you detect the text is already in {target_language}, just pass it through without trying to translate it yet.
    Make it easier to understand, using simpler words and shorter sentences if possible.

    Original Text:
    "{text_to_process}"

    Simplified Text:"""

    print(f"--- Requesting Simplification (for translation to {target_language}) ---")
    simplified_text = None
    try:
        response_simplify = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=simplify_prompt
        )
        
        if response_simplify.text:
            simplified_text = response_simplify.text.strip()
            print("--- Simplification Successful ---")
            print(f"Simplified intermediate text: {simplified_text}")
            
            if "unintelligible" in simplified_text.lower() or "gibberish" in simplified_text.lower() or "simplification is impossible" in simplified_text.lower():
                return "Sorry, the OCR couldn't properly recognize the text in your image. This often happens with non-English text like Hindi or Marathi. Try a clearer image or different file format."
        else:
            print("Warning: Received an empty or blocked response during simplification.")
            print(f"Simplification Response: {response_simplify}")
            return "Sorry, I couldn't process your request. The text may be gibberish or unrecognizable."
    except Exception as e:
        print(f"An error occurred during simplification: {e}")
        return "Sorry, I couldn't process your request due to an error during simplification."

    if not simplified_text:
         print("Skipping translation because simplification failed or produced empty text.")
         return "Sorry, I couldn't process your request because the simplification step failed."

    translate_prompt = f"""Translate the following text into {target_language}:
    If the text is already in {target_language}, just return it as is.

    Text to Translate:
    "{simplified_text}"

    {target_language} Translation:"""

    print(f"--- Requesting Translation to {target_language} ---")
    translated_text = None
    try:
        response_translate = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=translate_prompt
        )
        
        if response_translate.text:
            translated_text = response_translate.text.strip()
            print(f"--- Translation to {target_language} Successful ---")
            return translated_text
        else:
            print(f"Warning: Received an empty or blocked translation response for {target_language}.")
            print(f"Translation Response: {response_translate}")
            return "Sorry, I couldn't translate the text to the requested language."
    except Exception as e:
        print(f"An error occurred during translation to {target_language}: {e}")
        return "Sorry, an error occurred while translating your text."



