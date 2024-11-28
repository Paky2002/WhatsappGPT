from threading import Lock
import json
import os

class WaapiQueue:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        project_dir = os.path.abspath(os.path.dirname(__file__))  # Cartella in cui risiede questo script
        self._file_path = os.path.join(project_dir, "waapi_queue.json")
        
        # Initialize the file if it doesn't exist
        if not os.path.exists(self._file_path):
            with open(self._file_path, "w") as file:
                json.dump({}, file, indent=4)

    def _load_from_file(self):
        """Loads messages from the JSON file."""
        with open(self._file_path, "r") as file:
            return json.load(file)

    def _save_to_file(self, messages):
        """Saves the current state of the queue to a JSON file."""
        with open(self._file_path, "w") as file:
            json.dump(messages, file, indent=4)

    def add_message(self, phone_number: str, content: str, time: str, thread_id: str):
        """Adds a message for a specific phone number, sorted by time."""
        # Load current messages from file
        messages = self._load_from_file()

        if phone_number not in messages:
            messages[phone_number] = []
        
        # Add the new message
        messages[phone_number].append({"content": content, "time": time, "thread_id": thread_id})
        
        # Sort messages by time
        messages[phone_number].sort(key=lambda msg: msg["time"])
        
        # Save back to the file
        self._save_to_file(messages)

    def get_messages(self, phone_number: str):
        """Retrieves all messages for a specific phone number."""
        # Load messages from file
        messages = self._load_from_file()
        return messages.get(phone_number, [])

    def clear_messages(self, phone_number: str):
        """Clears all messages for a specific phone number and updates the file."""
        # Load messages from file
        messages = self._load_from_file()
        
        if phone_number in messages:
            del messages[phone_number]
        
        # Save back to the file
        self._save_to_file(messages)

    def get_phone_numbers(self):
        """Restituisce una lista di numeri di telefono dalla coda dei messaggi"""
        try:
            with open(self._file_path, "r") as file:
                data = json.load(file)
                
                # Estrae tutte le chiavi principali (i numeri di telefono) dal file JSON
                phone_numbers = list(data.keys())
                
                return phone_numbers
        except Exception as e:
            print(f"Errore nel caricare o nel leggere il file JSON: {e}")
            return []

    def print_queue(self):
        """Prints the entire queue in a well-formatted manner."""
        # Load messages from file
        messages = self._load_from_file()

        if not messages:
            print("Queue is empty.")
            return
        for phone_number, msgs in messages.items():
            print(f"Phone Number: {phone_number}")
            for msg in msgs:
                print(f"  - Time: {msg['time']}, Thread ID: {msg['thread_id']}, Content: {msg['content']}")

    def has_messages(self):
        """Checks if there are any messages in the JSON file."""
        # Load messages from file
        messages = self._load_from_file()
        
        # Check if there are any messages
        return bool(messages)
