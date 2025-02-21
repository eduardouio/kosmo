import openai
import json
from common.secrets import GPT_API_KEY
from common.AppLoger import logging_message, logging_error


class GPTProcessor:
    _api_key = GPT_API_KEY

    def __init__(self):
        logging_message('Inicializando GPTProcessor')
        self.client = openai.OpenAI(api_key=self._api_key)
        self.dispo = ''
        self.assistant = self.client.beta.assistants.retrieve(
            "asst_vVqU2SOi7jJefVllFWGqtoop"
        )
        self.thread = self.client.beta.threads.create()
        self._initialized = True

    def process_text(self, dispo):
        logging_message('Procesando texto')
        logging_message(dispo)
        self.dispo = dispo
        try:
            logging_message('Creando y ejecutando hilo')
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                additional_messages=[{"role": "user", "content": self.dispo}],
                temperature=0.01
            )
            logging_message('Hilo creado y ejecutado')
            logging_message(run)
            logging_message('Obteniendo mensajes del hilo')
            logging_message(self.client)
            thread_messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id)
            messages = thread_messages.model_dump()
            data = json.loads(messages['data'][0]['content'][0]['text']['value'])
            data = data[next(iter(data.keys()))]
            return data
        except Exception as e:
            logging_error('Error al procesar texto: {}'.format(str(e)))
            logging_error(messages['data'][0]['content'][0]['text']['value'])
            raise Exception('Error al procesar texto: {}'.format(str(e)))
