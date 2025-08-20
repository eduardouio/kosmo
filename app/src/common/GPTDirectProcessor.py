from openai import OpenAI
from common.secrets import GPT_API_KEY
from common.AppLoger import loggin_event
from common.TextPrepare import TextPrepare
import time
import json
import os

# Evitar importación circular - importar solo cuando sea necesario
# from partners.models import Partner


class GPTDirectProcessor:
    _api_key = GPT_API_KEY
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _prompt = None
    _client = None

    @property
    def client(self):
        if self._client is None:
            # Establece la variable de entorno antes de crear el cliente
            os.environ["OPENAI_API_KEY"] = self._api_key
            self._client = OpenAI()  # No pasar api_key aquí
        return self._client

    def process_text(self, dispo, partner=None):
        dispo = TextPrepare().process(dispo)

        if not self._prompt:
            self._load_prompt(partner)

        loggin_event('Iniciando procesamiento de texto')
        start_time = time.time()
        response = self.client.chat.completions.create(
            model="gpt-5-nano-2025-08-07",
            temperature=0,
            messages=[
                {"role": "system", "content": self._prompt},
                {"role": "user", "content": dispo}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "parse_stock_lines",
                        "description": "Parse stock lines into structured format",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "cantidad": {"type": "integer"},
                                            "modelo": {"type": "string"},
                                            "variedades": {"type": "array", "items": {"type": "string"}},
                                            "medidas": {"type": "array", "items": {"type": "number"}},
                                            "tallos": {"type": "array", "items": {"type": "number"}},
                                            "precios": {"type": "array", "items": {"type": "number"}}
                                        },
                                        "required": ["cantidad", "modelo", "variedades", "medidas", "tallos", "precios"]
                                    }
                                }
                            },
                            "required": ["items"]
                        }
                    }
                }
            ],
            tool_choice={"type": "function", "function": {
                "name": "parse_stock_lines"}}
        )

        laps_time = time.time() - start_time
        loggin_event(f'Respuesta recibida de OpenAI API {laps_time}s')

        if not response.choices[0].message.tool_calls:
            raise Exception("No se recibió un JSON válido desde la función")

        tool_call = response.choices[0].message.tool_calls[0]
        parsed = json.loads(tool_call.function.arguments)

        if not isinstance(parsed, dict) or "items" not in parsed:
            raise Exception(
                f"Formato inválido: se esperaba diccionario con 'items'")

        result_arrays = []
        required_fields = ["cantidad", "modelo",
                           "variedades", "medidas", "tallos", "precios"]

        for item in parsed["items"]:
            if not all(field in item for field in required_fields):
                missing = [f for f in required_fields if f not in item]
                raise Exception(f"Campos faltantes: {missing}")

            result_arrays.append([
                item["cantidad"],
                item["modelo"],
                item["variedades"],
                item["medidas"],
                item["tallos"],
                item["precios"]
            ])

        loggin_event(f'Procesados {len(result_arrays)} items')
        return result_arrays

    def _load_prompt(self, partner=None):
        # Primero intentar cargar desde el campo prompt_disponibility del partner
        if partner and hasattr(partner, 'prompt_disponibility') and partner.prompt_disponibility:
            self._prompt = partner.prompt_disponibility.strip()
            loggin_event(
                'Prompt cargado desde el campo prompt_disponibility del partner')
            return

        # Si no hay prompt personalizado, cargar desde archivo
        promt_file = os.path.join(self._current_dir, 'PromtText.txt')
        if not os.path.exists(promt_file):
            raise Exception('No se encontró el archivo de configuración')

        with open(promt_file, 'r', encoding='utf-8') as file:
            self._prompt = file.read()
        loggin_event('Archivo de configuración leído correctamente')
