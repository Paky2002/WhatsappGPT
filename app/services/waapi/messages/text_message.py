from .message import Message

class TextMessage(Message):
    """Text message type, inheriting from Message base class."""

    def __init__(self, message, preview_link=True):
        """Initialize with the message content and preview link option."""
        if not isinstance(message, str):  # Ensure the message is a string
            raise ValueError("Message content must be a string.")
        self.message = message
        self.preview_link = preview_link

    def get_payload(self):
        """Return the payload for a text message."""
        return {
            "message": self.message,
            "previewLink": self.preview_link
        }

    def get_message_type(self):
        """Return the message type ('text' for TextMessage)."""
        return "text"
