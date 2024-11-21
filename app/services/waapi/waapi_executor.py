import os
import requests
from flask import current_app
from dotenv import load_dotenv
from .messages.message import Message

# Load .env file to get environment variables
load_dotenv()

class WaapiExecutor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WaapiExecutor, cls).__new__(cls)
            # Read configuration from .env
            cls._instance.api_url = os.getenv('WAAPI_API_URL')
            cls._instance.bearer_token = os.getenv('WAAPI_BEARER_TOKEN')
            cls._instance.instance_id = os.getenv('WAAPI_INSTANCE_ID')  # New attribute for instanceId
        return cls._instance

    def __init__(self):
        # Use app context to initialize logger
        self.logger = None  # Initialize as None
        if current_app and hasattr(current_app, 'logger'):
            self.logger = current_app.logger  # Initialize logger only when inside app context

    def _get_headers(self):
        """ Helper method to build the headers for the API requests. """
        if self.logger:
            self.logger.debug("Building request headers.")
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.bearer_token}"
        }

    def _send_request(self, endpoint, method="POST", payload=None):
        """ General helper method to send requests to the Waapi API. """
        url = f"{self.api_url}/instances/{self.instance_id}/{endpoint}"  # Include instanceId in the URL
        headers = self._get_headers()
        if self.logger:
            self.logger.info(f"Sending {method} request to {url} with payload: {payload}")

        try:
            response = requests.request(method, url, headers=headers, json=payload)

            # Log the response status
            if self.logger:
                self.logger.info(f"Received response: {response.status_code} - {response.text}")

            # Check if the request was successful
            if response.status_code != 200:
                if self.logger:
                    self.logger.error(f"Request failed: {response.status_code} - {response.text}")
                raise Exception(f"Error: {response.status_code} - {response.text}")
            return response.json()

        except Exception as e:
            if self.logger:
                self.logger.exception("Error while sending request to Waapi API.")
            raise e  # Re-raise the exception after logging

    def send_message(self, chat_id, message: "Message"):
        """ Send a message using the provided Message object. """
        if not isinstance(message, Message):
            if self.logger:
                self.logger.error("The provided message is not a valid Message object.")
            raise ValueError("The provided message must be a valid Message object.")

        # Create the payload using the message's specific payload
        payload = message.get_payload()

        # Include the chatId as part of the payload in the send message request
        payload["chatId"] = f"{chat_id}@c.us"

        endpoint = "client/action/send-message"
        return self._send_request(endpoint, method="POST", payload=payload)
