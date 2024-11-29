from services.waapi.queue.waapi_queue import WaapiQueue
from services.waapi.waapi_executor import WaapiExecutor
from services.GPTAssistant.gpt_assistant_executor import GPTAssistantExecutor
from services.waapi.messages.message_factory import MessageFactory
from time import sleep
from time import sleep, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

def WAAPI_send_message(GPT_last_message, phone_number):
    # Crea il messaggio di risposta da inviare tramite Waapi
    message = MessageFactory.create_message("text", GPT_last_message)

    try:
        response = WAAPI_executor.send_message(phone_number, message)
    except Exception as e:
        print(f"Errore nell'invio del messaggio: {e}")


def doJob():
    processed_ids = []  # Lista per raccogliere gli ID dei messaggi elaborati

    for phone_number in queue.get_phone_numbers():
        # Ottieni tutti i messaggi per il numero di telefono
        m = queue.get_messages(phone_number)

        # Se non ci sono messaggi, passa al prossimo numero
        if not m:
            continue

        # Ordina i messaggi per timestamp decrescente
        sorted_messages = sorted(m, key=lambda msg: msg["time"], reverse=True)

        # Recupera l'ultimo messaggio (quello con il timestamp più recente)
        latest_message = sorted_messages[0]

        # Ottieni il timestamp attuale
        current_timestamp = int(time())

        print(f'{current_timestamp} - {latest_message["time"]} = {current_timestamp - latest_message["time"]}')
        if current_timestamp - latest_message["time"] < 5:
            continue  # Passa al prossimo numero di telefono

        # Processa i messaggi
        all_messages = " ".join([message["content"] for message in m])
        thread_id = latest_message['thread_id']

        GPT_message_obj = gpt_assistant_executor.create_message(thread_id, all_messages)
        GPT_run_obj = gpt_assistant_executor.create_run(thread_id)

        GPT_last_message = ''

        try:
            GPT_results = gpt_assistant_executor.run(
                thread_id,
                GPT_run_obj.id
            )

            print(GPT_results)

            if GPT_results.data:
                GPT_last_message = GPT_results.data[0]
                GPT_last_message = (
                    GPT_last_message.content[0].text.value if GPT_last_message.content else "ERRORE"
                )
            else:
                GPT_last_message = "No messages available"

            # Aggiungi gli ID dei messaggi elaborati a processed_ids
            for message in m:
                processed_ids.append(message['id'])

        except Exception as e:
            print(f"Errore nell'elaborazione del messaggio per il numero {phone_number}: {e}")
            # Aggiungi gli ID dei messaggi non elaborati ma comunque processati in errore
            for message in m:
                processed_ids.append(message['id'])

        # Elimina i messaggi elaborati dal database
        queue.clear_messages(phone_number, processed_ids)

        # Invia il messaggio tramite WAAPI
        WAAPI_send_message(GPT_last_message, phone_number)



# Ottieni la directory corrente del progetto
project_dir = os.path.abspath(os.path.dirname(__file__))  # Path assoluto della cartella corrente
db_path = os.path.join(project_dir, '..', 'instance', 'db.sqlite3')
db_engine = create_engine(f'sqlite:///{db_path}')

# Crea la sessione
Session = sessionmaker(bind=db_engine)
session = Session()

queue = WaapiQueue(session)
# Inizializza le istanze dei servizi
gpt_assistant_executor = GPTAssistantExecutor()
WAAPI_executor = WaapiExecutor()



# Loop principale
while True:
    if queue.has_messages():
        doJob()
    else:
        sleep(1)
    print('Eseguo un ciclo')