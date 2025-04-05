import openai
import json
from common.secrets import GPT_API_KEY
from common.AppLoger import loggin_event


class GPTProcessor:
    _api_key = GPT_API_KEY

    def __init__(self):
        loggin_event('Inicializando GPTProcessor')
        self.client = openai.OpenAI(api_key=self._api_key)
        self.dispo = ''
        self.assistant = self.client.beta.assistants.retrieve(
            "asst_vVqU2SOi7jJefVllFWGqtoop"
        )
        self.thread = None
        self._initialized = True

    def process_text(self, dispo):
        loggin_event('Intentar co Hilo anterior')
        if not self.thread:
            loggin_event('Creando hilo')
            self.thread = self.client.beta.threads.create()

        loggin_event('Procesando texto')
        loggin_event(dispo)
        self.dispo = dispo
        try:
            loggin_event('Creando y ejecutando hilo')
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                additional_messages=[{"role": "user", "content": self.dispo}],
                temperature=0.2
            )
            loggin_event('Hilo creado y ejecutado')
            loggin_event(run)
            loggin_event('Obteniendo mensajes del hilo')
            loggin_event(self.client)
            thread_messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id)
            messages = thread_messages.model_dump()
            data = json.loads(messages['data'][0]
                              ['content'][0]['text']['value'])
            data = data[next(iter(data.keys()))]
            return data
        except Exception as e:
            if 'thread_messages' in locals():
                loggin_event(f"Contenido del mensaje: {thread_messages}",
                             error=True
                             )
            loggin_event(
                'Error al procesar texto: {}'.format(str(e)), error=True
            )
            raise Exception('Error al procesar texto: {}'.format(str(e)))
