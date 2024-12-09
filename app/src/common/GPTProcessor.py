import openai
import json


class GPTProcessorError(Exception):
    pass


class GPTProcessor:
    _instance = None
    _api_key = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GPTProcessor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.client = openai.OpenAI(api_key=self._api_key)
        self.dispo = ''
        self.assistant = self.client.beta.assistants.retrieve(
            "asst_vVqU2SOi7jJefVllFWGqtoop"
        )
        self.thread = self.client.beta.threads.create()
        self._initialized = True

    def process_text(self, dispo):
        self.dispo = dispo
        try:
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                additional_messages=[{"role": "user", "content": self.dispo}],
                temperature=0
            )
            thread_messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id)
            messages = thread_messages.model_dump()
            data = messages['data'][0]['content'][0]['text']['value']
            data = data.replace('[\n[', '[')
            data = data.replace(']\n]', ']')
            data = data.split(',\n')
            data = [json.loads(i) for i in data]
            return data
        except Exception as e:
            return 'Error al procesar stock, no se puede leer el formato {}'.format(
                str(e)
            )
