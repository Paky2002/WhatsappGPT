from collections import deque
from threading import Lock

class WaapiQueue:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        """Implementazione del pattern Singleton."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.queue_map = {}  # Dizionario per memorizzare le code per ogni numero
            return cls._instance

    def push(self, phone_number, runId):
        """Aggiungi un runId alla coda associata al numero di telefono."""
        if phone_number not in self.queue_map:
            self.queue_map[phone_number] = deque()
        
        self.queue_map[phone_number].append(runId)
    
    def pop(self, phone_number):
        """Rimuove e restituisce il primo runId nella coda associata al numero di telefono."""
        if phone_number not in self.queue_map or not self.queue_map[phone_number]:
            print(f"Nessun runId da elaborare per il numero {phone_number}.")
            return None
        
        return self.queue_map[phone_number].popleft()

    def has_run_id(self, phone_number):
        """Controlla se ci sono runId nella coda per il numero specificato."""
        return phone_number in self.queue_map and len(self.queue_map[phone_number]) > 0

    def remove_run_id(self, phone_number, runId):
        """Rimuove un runId specifico dalla coda associata al numero di telefono."""
        if phone_number in self.queue_map:
            try:
                # Rimuovi il runId dalla coda
                self.queue_map[phone_number].remove(runId)
                print(f"RunId {runId} rimosso dalla coda per il numero {phone_number}.")
            except ValueError:
                print(f"RunId {runId} non trovato nella coda per il numero {phone_number}.")
        else:
            print(f"Nessun runId per il numero {phone_number}.")

    def print_queue(self):
        """Stampa tutte le code per ogni numero di telefono."""
        for phone_number, queue in self.queue_map.items():
            print(f"Numero: {phone_number}, Coda: {list(queue)}")