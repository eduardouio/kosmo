import openai
from common.secrets import GPT_API_KEY
from common.AppLoger import loggin_event
import os


class GPTProcessor:
    _api_key = GPT_API_KEY
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _promnt = None

    def __init__(self):
        loggin_event('Inicializando GPTProcessor')
        loggin_event('Directorio Base')
        openai.api_key = self._api_key
        self._initialized = True

    def process_text(self, dispo):
        promt_file = os.path.join(self._current_dir, 'PromtText.txt')
        if os.path.exists(promt_file):
            with open(promt_file, 'r', encoding='utf-8') as file:
                self.prompt = file.read()
                loggin_event('Archivo de configuración leído correctamente')

        if not self.prompt:
            raise Exception('No se encontró el archivo de configuración')

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": dispo}
                ],
                temperature=0.1,
                max_tokens=2000,
                n=1,
                stop=None
            )

            loggin_event('Respuesta recibida de OpenAI API')
            loggin_event(response)

            # Procesar la respuesta
            message = response['choices'][0]['message']['content']
            return message.strip()

        except Exception as e:
            loggin_event(f"Error al procesar texto: {str(e)}", error=True)
            raise Exception(f"Error al procesar texto: {str(e)}")
