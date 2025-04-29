from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create the Flask application
app = create_app()

if __name__=="__main__":
    app.run(debug=True,port=5000,host='0.0.0.0')
