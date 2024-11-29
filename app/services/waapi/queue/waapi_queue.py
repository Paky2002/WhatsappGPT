from threading import Lock
import json
import os
from models.messages import Message

class WaapiQueue:
    _instance = None
    _lock = Lock()

    def __new__(cls, session, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.session = session
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        project_dir = os.path.abspath(os.path.dirname(__file__))  # Cartella in cui risiede questo script
        self._file_path = os.path.join(project_dir, "waapi_queue.json")
        
        # Initialize the file if it doesn't exist
        if not os.path.exists(self._file_path):
            with open(self._file_path, "w") as file:
                json.dump({}, file, indent=4)

    def add_message(self, phone_number: str, content: str, time: int, thread_id: str):
        """Aggiunge un messaggio per un numero di telefono specifico, ordinato per tempo."""
        try:
            # Crea un nuovo oggetto Message
            message = Message(
                phone_number=phone_number,
                content=content,
                time=time,
                thread_id=thread_id
            )

            # Aggiungi il messaggio al database
            self.session.add(message)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Errore durante l'aggiunta del messaggio: {e}")

    def get_messages(self, phone_number: str):
        """Recupera tutti i messaggi per un numero di telefono specifico, ordinati per tempo."""
        try:
            # Recupera i messaggi per il numero di telefono specificato e ordina per 'time'
            messages = self.session.query(Message).filter_by(phone_number=phone_number).order_by(Message.time.asc()).all()

            # Restituisce i messaggi in una lista di dizionari
            return [{"id": msg.id, "content": msg.content, "time": msg.time, "thread_id": msg.thread_id} for msg in messages]
        except Exception as e:
            print(f"Errore durante il recupero dei messaggi: {e}")
            return []

    def clear_messages(self, phone_number: str, processed_ids: list):
        """Elimina i messaggi che sono stati elaborati per un numero di telefono, evitando quelli non ancora processati."""
        try:
            # Elimina solo i messaggi che sono stati elaborati (i cui ID sono in processed_ids)
            rows_deleted = self.session.query(Message).filter(
                Message.phone_number == phone_number,
                Message.id.in_(processed_ids)  # Solo i messaggi che hanno un ID in processed_ids
            ).delete()

            if rows_deleted > 0:
                print(f"Eliminati {rows_deleted} messaggi elaborati per il numero {phone_number}.")
            else:
                print(f"Nessun messaggio elaborato trovato per il numero {phone_number}.")
            
            # Commit delle modifiche al database
            self.session.commit()

        except SQLAlchemyError as e:
            print(f"Errore nel rimuovere i messaggi dal database: {e}")


    def get_phone_numbers(self):
        """Restituisce una lista di numeri di telefono dalla coda dei messaggi nel database."""
        try:
            # Recupera tutti i numeri di telefono unici dalla tabella 'Message'
            phone_numbers = self.session.query(Message.phone_number).distinct().all()
            
            # Estrae solo i numeri di telefono dalla lista di tuple restituita
            phone_numbers = [phone_number[0] for phone_number in phone_numbers]
            
            return phone_numbers
        except SQLAlchemyError as e:
            print(f"Errore nel caricare i numeri di telefono dal database: {e}")
            return []


    def print_queue(self):
        """Prints the entire queue in a well-formatted manner from the database."""
        try:
            # Recupera tutti i messaggi dal database, ordinati per numero di telefono e per time
            messages = self.session.query(Message.phone_number, Message.content, Message.time, Message.thread_id).order_by(Message.phone_number, Message.time).all()

            if not messages:
                print("Queue is empty.")
                return
            
            current_phone_number = None
            
            # Stampa ogni messaggio in modo formattato
            for phone_number, content, time, thread_id in messages:
                if phone_number != current_phone_number:
                    if current_phone_number is not None:
                        print()  # Aggiungi una riga vuota tra i gruppi di numeri di telefono
                    print(f"Phone Number: {phone_number}")
                    current_phone_number = phone_number

                print(f"  - Time: {time}, Thread ID: {thread_id}, Content: {content}")
    
        except SQLAlchemyError as e:
            print(f"Errore nel caricare i messaggi dal database: {e}")

    def has_messages(self):
        """Checks if there are any messages in the database."""
        try:
            # Verifica se esistono messaggi nel database
            result = self.session.query(Message).first()  # Recupera il primo messaggio
            return result is not None  # Se c'è almeno un messaggio, ritorna True, altrimenti False
        except SQLAlchemyError as e:
            print(f"Errore nel controllo dei messaggi: {e}")
            return False
