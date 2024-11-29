from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from extensions import db


# Modello per rappresentare i messaggi
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)  # ID univoco per ogni messaggio
    phone_number = db.Column(db.String(20), nullable=False)  # Numero di telefono
    content = db.Column(db.String(500), nullable=False)  # Contenuto del messaggio
    time = db.Column(db.Integer, nullable=False)  # Timestamp del messaggio
    thread_id = db.Column(db.String(100), nullable=False)  # ID del thread

    def __repr__(self):
        return f"<Message {self.phone_number} - {self.content[:20]}>"