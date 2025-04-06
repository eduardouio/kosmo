from openai import OpenAI
from common.secrets import GPT_API_KEY
from common.AppLoger import loggin_event
from common.TextPrepare import TextPrepare
import time
import json
import os


class GPTDirectProcessor:
    _api_key = GPT_API_KEY
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _promt = None
    _client = OpenAI(api_key=_api_key)

    def process_text(self, dispo):
        dispo = TextPrepare().process(dispo)
        promt_file = os.path.join(self._current_dir, 'PromtText.txt')
        if os.path.exists(promt_file):
            with open(promt_file, 'r', encoding='utf-8') as file:
                self._prompt = file.read()
                loggin_event('Archivo de configuración leído correctamente')

        if not self._prompt:
            raise Exception('No se encontró el archivo de configuración')
        loggin_event('Iniciando procesamiento de texto')
        start_time = time.time()

        try:
            response = self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._prompt},
                    {"role": "user", "content": dispo}
                ],
            )
            end_time = time.time()
            laps_time = end_time - start_time
            loggin_event(f'Respuesta recibida de OpenAI API {laps_time}')
            loggin_event(response)

            # Procesar la respuesta
            message = response.choices[0].message.content
            message = json.loads(message)
            return message

        except Exception as e:
            loggin_event('Error en la API de OpenAI', error=True)
            loggin_event(f"Error al procesar texto: {str(e)}", error=True)
            loggin_event(response, error=True)
            raise Exception(f"Error al procesar texto: {str(e)}")
