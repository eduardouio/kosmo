import openai
import json


class GPTProcessorError(Exception):
    pass


class GPTProcessor:
    _instance = None
    _api_key = "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"

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
            processed_data = json.loads(
                messages['data'][0]['content'][0]['text']['value'])
            return processed_data
        except Exception as e:
            raise GPTProcessorError(
                'Error al procesar el texto'.format(str(e))
            )
