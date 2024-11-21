from abc import ABC, abstractmethod

class Message(ABC):
    """Base class for all message types."""

    @abstractmethod
    def get_payload(self):
        """Method to return the specific payload of the message."""
        pass

    @abstractmethod
    def get_message_type(self):
        """Returns the type of message (e.g., 'text', 'image', etc.)."""
        pass
