from flask import Blueprint, render_template, request, jsonify
import requests

# Crea un blueprint per le rotte di test
test_bp = Blueprint("test", __name__)

@test_bp.route("/test_chat", methods=["GET", "POST"])
def test_chat():
    if request.method == "POST":

        print ("MI E ARRIVATO UN MESSAGGIO")

        # Ottieni i dati dal form
        phone_number = request.form.get("phone_number")
        message_content = request.form.get("message_content")

        if not phone_number or not message_content:
            return jsonify({"success": False, "error": "Numero di telefono e messaggio obbligatori"}), 400

        # Simula il payload di Waapi
        waapi_payload = {
            "event": "message",
            "instanceId": "33",
            "data": {
                "message": {
                    "_data": {
                        "id": {
                            "fromMe": False,
                            "remote": f"{phone_number}@c.us",
                            "id": "TEST_MESSAGE_ID",
                            "_serialized": f"false_{phone_number}@c.us_TEST_MESSAGE_ID"
                        },
                        "body": message_content,
                        "type": "chat",
                        "t": 1669994807,
                        "notifyName": "Test User",
                        "from": f"{phone_number}@c.us",
                        "to": "50611223355@c.us",
                        "self": "in",
                        "ack": 1,
                        "isNewMsg": True,
                        "star": False,
                        "broadcast": False
                    },
                    "id": {
                        "fromMe": False,
                        "remote": f"{phone_number}@c.us",
                        "id": "TEST_MESSAGE_ID",
                        "_serialized": f"false_{phone_number}@c.us_TEST_MESSAGE_ID"
                    },
                    "body": message_content,
                    "type": "chat",
                    "timestamp": 1669994807,
                    "from": f"{phone_number}@c.us",
                    "to": "50611223355@c.us",
                    "deviceType": "ios",
                    "isForwarded": False
                }
            }
        }

        # Invia il payload alla route webhook
        try:
            response = requests.post("http://localhost:5000/main/recived_message", json=waapi_payload)
            response_data = response.json()
            return jsonify(response_data), response.status_code
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return render_template("test_chat.html")
