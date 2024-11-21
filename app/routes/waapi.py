from flask import Blueprint, request, render_template, current_app, jsonify
from services.waapi.messages.message_factory import MessageFactory

# Create the blueprint for Waapi routes
waapi = Blueprint("waapi", __name__)

@waapi.route("/test-send-text-message", methods=["GET", "POST"])
def send_message():
    """Route to send a message to Waapi."""
    response = None
    if request.method == "POST":
        chat_id = request.form.get("chatId")
        message = MessageFactory.create_message("text", request.form.get("message"))

        # Get the instance of WaapiExecutor
        waapi_executor = current_app.waapi_executor

        try:
            # Call the method to send the message
            response = waapi_executor.send_message(chat_id, message)
        except Exception as e:
            current_app.logger.error(f"Error sending message: {e}")
            response = {"error": "Message sending failed"}

    return render_template("send_message.html", response=response)
