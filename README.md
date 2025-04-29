# SimplifAI Backend

A Flask backend for OCR and text processing with Gemini AI integration.

## Development Setup

### Prerequisites
- Python 3.10+
- UV for package management
- Tesseract OCR installed locally

### Installation
1. Clone the repository
2. Set up a virtual environment:
   ```
   uv venv
   ```
3. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   OCR_SPACE_API_KEY=your_ocr_space_api_key
   ```
5. Run the development server:
   ```
   python run.py
   ```

## Deployment to Render

### Automatic Deployment with Blueprint
This repository includes a `render.yaml` file that configures the deployment.

1. Fork or clone this repository to your GitHub account
2. Create a new Render account or log in to your existing account
3. On Render dashboard, click "New" and select "Blueprint"
4. Connect your GitHub account and select this repository
5. Render will detect the `render.yaml` file and set up the service
6. Add the required environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `OCR_SPACE_API_KEY`: Your OCR.space API key
7. Click "Apply" to deploy the service

### Manual Deployment
1. Fork or clone this repository to your GitHub account
2. Create a new Render account or log in to your existing account
3. On Render dashboard, click "New" and select "Web Service"
4. Connect your GitHub account and select this repository
5. Configure the service:
   - **Name**: Choose a name for your service
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
6. Add the required environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `OCR_SPACE_API_KEY`: Your OCR.space API key
7. Click "Create Web Service" to deploy

## API Endpoints

- `/process-and-simplify`: Process and simplify documents
- `/tools/translate`: Translate text to different languages
- `/tools/summarize`: Summarize text content
- `/tools/grammar-corrector`: Fix grammar and spelling
- `/tools/word-meaning`: Get word definitions and examples

## Environment Setup

The server requires the following environment variables:

```
# API Keys
GEMINI_API_KEY=your_gemini_api_key
OCR_SPACE_API_KEY=your_ocr_space_api_key

# Optional Configuration
DEBUG=True
PORT=5000
HOST=0.0.0.0
```

You can create a `.env` file in the root directory with these values.

## OCR.space API Integration

The application now uses OCR.space API for text extraction instead of local Tesseract OCR. This provides several benefits:

1. Better accuracy for detecting Indic scripts (Hindi, Marathi, etc.)
2. No local dependencies or installation required
3. Improved processing speed
4. More reliable character recognition

### OCR.space API Key

You need to obtain an API key from [OCR.space](https://ocr.space/ocrapi) and add it to your `.env` file as `OCR_SPACE_API_KEY`.

The free tier allows for 25,000 requests per month, which should be sufficient for most use cases.

## Simplified Usage

The API endpoint `/process-and-simplify` accepts a JSON payload with the following fields:

```json
{
  "file_url": "https://example.com/path/to/document.pdf",
  "language": "Hindi"
}
```

The server will:
1. Extract text from the document using OCR.space API
2. Simplify the text using Google's Gemini API
3. Translate to the target language if needed

## Supported File Formats

- Images: PNG, JPG, JPEG, GIF, BMP, TIFF
- Documents: PDF, DOCX

## Supported Languages

- English
- Hindi
- Marathi
- Tamil
- Telugu
- Bengali
- Gujarati
- Kannada
- Malayalam
- Punjabi
- Urdu
