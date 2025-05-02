from dotenv import load_dotenv
from flask import Flask
from app.routes.process import process_bp
from app.routes.tools import tools
from flask_cors import CORS


load_dotenv()

def create_app():
    app=Flask(__name__)
    CORS(app,supports_credentials=True)
    app.register_blueprint(process_bp)
    app.register_blueprint(tools)


    return app
