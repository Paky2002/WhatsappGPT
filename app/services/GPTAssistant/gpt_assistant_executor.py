from flask import current_app
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

# Load .env file to get environment variables
load_dotenv()

class GPTAssistantExecutor :
    _instance = None

    def __new__(cls):
        """Override del metodo __new__ per implementare il pattern Singleton."""
        if cls._instance is None:
            cls._instance = super(GPTAssistantExecutor, cls).__new__(cls)
            # Read configuration from .env
            cls._instance.openAI = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))
            cls._instance.assistantId = os.getenv("OPEN_AI_GPT_ASSISTANT_ID")
            return cls._instance

    def __repr__(self):
        return f"GPTAssistant API(clientId={self.openAI}, assistantId={self.assistantId})"

    def __init__(self):
        # Use app context to initialize logger
        self.logger = None  # Initialize as None
        if current_app and hasattr(current_app, 'logger'):
            self.logger = current_app.logger  # Initialize logger only when inside app context

    def create_thread (self) :
        return self.openAI.beta.threads.create()

    def retrieve_thread (self, thread_id) :
        return self.openAI.beta.threads.retrieve(thread_id)

    def create_message (self, thread_id, user_message) :
        return self.openAI.beta.threads.messages.create(
            thread_id,
            role="user",
            content=user_message,
        )

    def get_all_messages (self, thread_id) :
        return self.openAI.beta.threads.messages.list(thread_id)


    def create_run (self, thread_id) :
        return self.openAI.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.get_assistant().id
        )

    def get_run (self, thread_id, run_id) :
        return self.openAI.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

    def get_status_run (self, thread_id, run_id) :
        return self.get_run(thread_id, run_id).status

    def get_assistant (self) :
        return self.openAI.beta.assistants.retrieve(self.assistantId)

    def send_user_message_to_assistant (self, user_message, thread_id=None) :
        
        if thread_id==None :
            thread_obj = self.create_thread()
        else :
            thread_obj = self.retrieve_thread(thread_id)

        message_obj = self.create_message(thread_obj.id, user_message)
        rub_obj = self.create_run(thread_obj.id)

        return message_obj, rub_obj
    
    def run (self, thread_id, run_id) : 

        run_status = self.get_run(thread_id, run_id).status

        while run_status == "in_progress" or run_status == "queued" :
            time.sleep(1)
            run_status = self.get_run(thread_id, run_id).status

        messages = self.get_all_messages(thread_id)

        return messages

