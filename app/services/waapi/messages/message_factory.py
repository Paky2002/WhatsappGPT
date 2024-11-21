# /services/message_factory.py

from .text_message import TextMessage

class MessageFactory:
    @staticmethod
    def create_message(message_type: str, *args, **kwargs):
        """ Factory method to create a message based on the type. """
        if message_type == "text":
            return TextMessage(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported message type: {message_type}")
