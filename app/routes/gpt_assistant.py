from flask import Blueprint, request, render_template, current_app, jsonify
from services.GPTAssistant.gpt_assistant_executor import GPTAssistantExecutor

# Create the blueprint for GPTAssistant routes
gpt_assistant_bp  = Blueprint("GPTAssistant", __name__)

@gpt_assistant_bp.route('/chat', methods=['GET', 'POST'])
def chat():
    """
    Serve a chat interface and handle chat interactions.
    """
    if request.method == 'POST':
        user_message = request.json.get('message')
        thread_id = request.json.get('thread_id', None)  # Optional: thread ID to continue a conversation

        try:
            # Use the executor to send the message and get a response
            messages = current_app.gpt_assistant_executor.send_user_message_to_assistant(user_message, 'thread_BziAoYhvDThJftO144U3rWJ9')

            # Extract the last message content
            if messages.data:
                last_message = messages.data[0]
                last_message_content = last_message.content[0].text.value if last_message.content else "No content"
            else:
                last_message_content = "No messages available"

            return jsonify({"success": True, "last_message": last_message_content})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # Render the chat interface for GET requests
    return render_template('chat.html')
