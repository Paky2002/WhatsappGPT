from services.waapi.queue.waapi_queue import WaapiQueue
from services.waapi.waapi_executor import WaapiExecutor
from services.GPTAssistant.gpt_assistant_executor import GPTAssistantExecutor
from services.waapi.messages.message_factory import MessageFactory
from time import sleep

def WAAPI_send_message (GPT_last_message, phone_number) :
    # Crea il messaggio di risposta da inviare tramite Waapi
    message = MessageFactory.create_message("text", GPT_last_message)

    try:
        response = WAAPI_executor.send_message(phone_number, message)
        
    except Exception as e:
        print(f"Errore nell'invio del messaggio: {e}")

def doJob():
    queue = WaapiQueue()

    for phone_number in queue.get_phone_numbers() : 
        m = queue.get_messages(phone_number)
        all_messages = " ".join([message["content"] for message in queue.get_messages(phone_number)])
        thread_id = m[0]['thread_id']
        GPT_message_obj = gpt_assistant_executor.create_message(thread_id, all_messages)
        GPT_run_obj = gpt_assistant_executor.create_run(thread_id)

        GPT_last_message = ''

        print(f'#1 thread_id = {thread_id} GPT_run_obj = {GPT_run_obj} GPT_message_obj = {GPT_message_obj}')

        try:    
            GPT_results = gpt_assistant_executor.run(
                thread_id,
                GPT_run_obj.id
            )

            print('#2')

            if GPT_results.data:
                GPT_last_message = GPT_results.data[0]
                GPT_last_message = (
                    GPT_last_message.content[0].text.value if GPT_last_message.content else "ERRORE"
                )
            else:
                GPT_last_message = "No messages available"

            queue.clear_messages(phone_number)
        except Exception as e:
            print(f"Errore nell'invio del messaggio: {e}")
            queue.clear_messages(phone_number)

        WAAPI_send_message(GPT_last_message, phone_number)
        



queue = WaapiQueue()
gpt_assistant_executor = GPTAssistantExecutor()
WAAPI_executor = WaapiExecutor()

while True :
    print(queue.has_messages())
    if (queue.has_messages()) : 
        doJob()
    else :
        sleep(5)
    print('Eseguo un ciclo')