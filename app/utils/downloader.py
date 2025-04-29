import requests
import os
import tempfile
import uuid


def download_file_from_url(url):
    """
    Downloads a file from URL to a temporary directory with a unique filename.
    Returns the full path to the downloaded file.
    The caller is responsible for deleting the file after processing.
    """
    # Create a unique filename to avoid collisions
    original_filename = url.split("/")[-1]
    file_extension = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(tempfile.gettempdir(), 'simplifai_temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Full path to save the file
    temp_file_path = os.path.join(temp_dir, unique_filename)
    
    # Download the file
    response = requests.get(url)
    
    with open(temp_file_path, 'wb') as f:
        f.write(response.content)
    
    return temp_file_path