from flask import Blueprint, request, render_template, current_app, jsonify
from services.waapi.messages.message_factory import MessageFactory
from models.threads import Thread
from extensions import db
from time import sleep

# Create the blueprint for Waapi routes
main_bp = Blueprint("main", __name__)

def send_message (gptMessage, message_sender_phone_number) :
    # Crea il messaggio di risposta da inviare tramite Waapi
    message = MessageFactory.create_message("text", gptMessage)

    try:
        response = current_app.waapi_executor.send_message(message_sender_phone_number, message)
        return jsonify({"status": "success", "data": response}), 200
    except Exception as e:
        current_app.logger.error(f"Errore nell'invio del messaggio: {e}")
        return jsonify({"error": "Message sending failed", "details": str(e)}), 500

@main_bp.route("/recived_message", methods=["GET", "POST"])
def webhook():
    body = request.get_json()

    # Estrai i dati dal body
    instance_id = body.get('instanceId')
    event_name = body.get('event')
    event_data = body.get('data')

    if event_name == 'message':
        message_data = event_data.get('message')

        # Verifica che il tipo di messaggio sia 'chat'
        if message_data.get('type') == 'chat':
            message_sender_id = message_data.get('from')
            message_created_at = message_data.get('timestamp') * 1000  # converti da secondi a millisecondi
            message_content = message_data.get('body')

            # Estrai il numero di telefono dal mittente
            message_sender_phone_number = message_sender_id.replace('@c.us', '')

            # Controlla se esiste già un thread associato al numero di telefono
            existing_thread = Thread.query.filter_by(phone_number=message_sender_phone_number).first()

            if existing_thread:
                thread_id = existing_thread.thread_id

                # Controlla se il thread è attivo
                if not existing_thread.is_active:
                    return jsonify({"success": False, "error": "Thread not active"}), 400
            else:
                # Crea un nuovo thread
                try:
                    thread_obj = current_app.gpt_assistant_executor.create_thread()
                    thread_id = thread_obj.id

                    # Salva il nuovo thread nel database
                    new_thread = Thread(phone_number=message_sender_phone_number, thread_id=thread_id)
                    db.session.add(new_thread)
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Errore nella creazione del thread: {e}")
                    return jsonify({"success": False, "error": str(e)}), 500

            # Controlla se il contenuto del messaggio è "OPERATORE"
            if message_content.strip().upper() == "OPERATORE":
                try:
                    # Imposta il thread su inattivo
                    if existing_thread:
                        existing_thread.is_active = False
                    else:
                        new_thread.is_active = False
                    db.session.commit()

                    return jsonify({"status": "success", "message": "Thread disattivato"}), 200
                except Exception as e:
                    current_app.logger.error(f"Errore nell'aggiornamento del thread: {e}")
                    return jsonify({"success": False, "error": str(e)}), 500

            if current_app.waapi_queue.has_run_id (message_sender_phone_number) : 
                while current_app.waapi_queue.has_run_id(message_sender_phone_number):
                    sleep(2)  # Dormi per 1 secondo prima di verificare di nuovo

            message_obj = current_app.gpt_assistant_executor.create_message(thread_id, message_content)
            run_obj = current_app.gpt_assistant_executor.create_run(thread_id)
            
            print(run_obj.id, "  ->  ", message_obj.content)
            
            current_app.waapi_queue.push(message_sender_phone_number, run_obj.id)

            try:
                
                messages = current_app.gpt_assistant_executor.run(
                    thread_id,
                    run_obj.id
                )

                # Estrai l'ultimo messaggio di risposta
                if messages.data:
                    last_message = messages.data[0]
                    last_message_content = (
                        last_message.content[0].text.value if last_message.content else "No content"
                    )
                else:
                    last_message_content = "No messages available"

                current_app.waapi_queue.remove_run_id(message_sender_phone_number, run_obj.id)
            except Exception as e:
                current_app.waapi_queue.remove_run_id(message_sender_phone_number, run_obj.id)
                current_app.logger.error(f"Errore nell'interazione con GPT: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

            return send_message(last_message_content, message_sender_phone_number)

    return jsonify({"success": False, "error": "Invalid event type or data"}), 400
