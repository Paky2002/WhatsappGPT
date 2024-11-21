import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from services.GPTAssistant.gpt_assistant_executor import GPTAssistantExecutor
from config.config import Config
from services.waapi.waapi_executor import WaapiExecutor  
from services.waapi.queue.waapi_queue import WaapiQueue  # Importa WaapiExecutor
from extensions import db

def create_app():
    # Crea una nuova istanza Flask
    app = Flask(__name__)
    app.config.from_object(Config)  # Carica la configurazione da config.py

    # Inizializza SQLAlchemy
    db.init_app(app)

    # Configura il logging
    configure_logging(app)

    # Instanzia WaapiExecutor e salvalo su app
    app.waapi_executor = WaapiExecutor()

    # Instanzia GPTAssistantExecutor e salvalo su app
    app.gpt_assistant_executor = GPTAssistantExecutor()

    app.waapi_queue = WaapiQueue()

    # Registra le route
    from routes import register_routes
    register_routes(app)

    # Configura Flask-Admin
    configure_admin(app)

    with app.app_context():

        db.create_all()

    return app

def configure_logging(app):
    if app.config["LOG_TO_STDOUT"]:
        handler = logging.StreamHandler()
        handler.setLevel(app.config["LOG_LEVEL"])
    else:
        handler = logging.FileHandler(app.config["LOG_FILE"])
        handler.setLevel(app.config["LOG_LEVEL"])

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config["LOG_LEVEL"])

def configure_admin(app):
    from models.threads import Thread  # Importa il modello Thread

    # Crea un'istanza di Flask-Admin
    admin = Admin(app, name="Admin Panel", template_mode="bootstrap4")

    # Aggiungi il modello Thread al pannello di amministrazione
    admin.add_view(ModelView(Thread, db.session))
