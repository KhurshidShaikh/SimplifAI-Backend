from flask import Blueprint,request,jsonify
from app.services.gemini import load_api_key
from google import genai

tools=Blueprint("tools",__name__)
API_KEY=load_api_key()
client = genai.Client(api_key=API_KEY)

@tools.route("/tools/translate",methods=["POST"])
def translate():
    data=request.get_json()
    text=data.get("text")
    language=data.get("language")
    if not text or not language:
        return jsonify({
            "error": "please provide text and language both"
        })
    translate_prompt = f"""Translate the following text into {language}:
    If the text is already in {language}, just return it as is.

    Text to Translate:
    "{text}"
    {language} Translation:"""

    print(f"--- Requesting Translation to {language} ---")
    try:
        response_translate = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=translate_prompt
        )
        
        if response_translate.text:
            translated_text = response_translate.text.strip()
            print(f"--- Translation to {language} Successful ---")
            return jsonify({"translated_text":translated_text})
        else:
            print(f"Warning: Received an empty or blocked translation response for {language}.")
            print(f"Translation Response: {response_translate}")
            return jsonify({"error":"Sorry, I couldn't translate the text to the requested language."})
    except Exception as e:
        print(f"An error occurred during translation to {language}: {e}")
        return jsonify({"error":"Sorry, I couldn't translate the text to the requested language."})
    



@tools.route("/tools/summarize",methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text")
    
    if not text:
        return jsonify({
            "error":"please provide text to summarize"
        })
    
    summarize_prompt = f"""Please summarize the following text concisely while preserving the key points:

    Text to Summarize:
    "{text}"
    
    Summary:"""

    print("--- Requesting Text Summarization ---")
    try:
        response_summarize = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=summarize_prompt
        )
        
        if response_summarize.text:
            summary_text = response_summarize.text.strip()
            print("--- Summarization Successful ---")
            return jsonify({"summary": summary_text})
        else:
            print("Warning: Received an empty or blocked summarization response.")
            print(f"Summarization Response: {response_summarize}")
            return jsonify({"error":"Sorry, I couldn't summarize the provided text."})
    except Exception as e:
        print(f"An error occurred during summarization: {e}")
        return jsonify({"error":"Sorry, I couldn't summarize the provided text."})



@tools.route("/tools/grammar-corrector",methods=["POST"])
def grammar_corrector():
    data = request.get_json()
    text = data.get("text")
    
    if not text:
        return jsonify({
            "error":"please provide text to correct"
        })
    
    grammar_prompt = f"""Please correct any grammar, spelling, or punctuation errors in the following text.
    Return only the corrected text without explanations:

    Text to Correct:
    "{text}"
    
    Corrected Text:"""

    print("--- Requesting Grammar Correction ---")
    try:
        response_grammar = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=grammar_prompt
        )
        
        if response_grammar.text:
            corrected_text = response_grammar.text.strip()
            print("--- Grammar Correction Successful ---")
            return jsonify({"corrected_text": corrected_text})
        else:
            print("Warning: Received an empty or blocked grammar correction response.")
            print(f"Grammar Correction Response: {response_grammar}")
            return jsonify({"error":"Sorry, I couldn't correct the provided text."})
    except Exception as e:
        print(f"An error occurred during grammar correction: {e}")
        return jsonify({"error":"Sorry, I couldn't correct the provided text."})


@tools.route("/tools/word-meaning",methods=["POST"])
def word_meaning():
    data = request.get_json()
    word = data.get("word")
    
    if not word:
        return jsonify({
            "error":"please provide a word to look up"
        })
    
    meaning_prompt = f"""Please provide the meaning/definition of the following word.
    Also include part of speech, and a simple example sentence:

    Word: "{word}"
    
    Format the response as a JSON structure with fields: definition, part_of_speech, example"""

    print(f"--- Requesting Meaning for '{word}' ---")
    try:
        response_meaning = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=meaning_prompt
        )
        
        if response_meaning.text:
            meaning_text = response_meaning.text.strip()
            print(f"--- Meaning for '{word}' Retrieved Successfully ---")
            return jsonify({"result": meaning_text})
        else:
            print(f"Warning: Received an empty or blocked meaning response for '{word}'.")
            print(f"Meaning Response: {response_meaning}")
            return jsonify({"error":f"Sorry, I couldn't find the meaning of '{word}'."})
    except Exception as e:
        print(f"An error occurred while getting meaning for '{word}': {e}")
        return jsonify({"error":f"Sorry, I couldn't find the meaning of '{word}'."})

