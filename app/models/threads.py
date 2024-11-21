from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from extensions import db

class Thread(db.Model):
    __tablename__ = 'threads'

    id = db.Column(db.Integer, primary_key=True)  # Primary Key
    phone_number = db.Column(db.String(20), unique=True, nullable=False)  # User's phone number
    thread_id = db.Column(db.String(100), unique=True, nullable=False)  # Thread ID for GPT context
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Timestamp of when the thread was created
    is_active = db.Column(db.Boolean, default=True)  # Boolean flag to indicate if GPT should continue responding

    def __init__(self, phone_number, thread_id):
        self.phone_number = phone_number
        self.thread_id = thread_id

    @classmethod
    def is_phone_number_exist(cls, phone_number):
        """ Check if a phone number already exists in the database. """
        thread = cls.query.filter_by(phone_number=phone_number).first()
        return thread is not None

    def __repr__(self):
        return f'<Thread {self.phone_number}, ThreadID {self.thread_id}>'
