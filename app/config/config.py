import os

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')

    # Logging configuration
    LOG_TO_STDOUT = os.getenv("LOG_TO_STDOUT")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")  # Default log file name
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")  # You can set it to 'DEBUG', 'INFO', 'ERROR', etc.
    
    # Add the templates folder configuration (if not already set in your app)
    TEMPLATES_AUTO_RELOAD = True
    TEMPLATE_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')