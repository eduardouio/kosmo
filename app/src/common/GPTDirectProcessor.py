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

    tool_definitions = [
        {
            "type": "function",
            "function": {
                "name": "parse_stock_lines",
                "description": "Convierte múltiples líneas de stock floral en un array de objetos JSON",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "cantidad": { "type": "integer" },
                                    "modelo": { "type": "string" },
                                    "tallos_totales": { "type": "integer" },
                                    "precio_tallo_caja": { "type": "number" },
                                    "variedad": { "type": "string" },
                                    "medidas": {
                                        "type": "array",
                                        "items": { "type": "number" }
                                    },
                                    "precios": {
                                        "type": "array",
                                        "items": { "type": "number" }
                                    }
                                },
                                "required": [
                                    "cantidad",
                                    "modelo",
                                    "tallos_totales",
                                    "precio_tallo_caja",
                                    "variedad",
                                    "medidas",
                                    "precios"
                                ]
                            }
                        }
                    },
                    "required": ["items"]
                }
            }
        }
    ]

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
        loggin_event(f'Texto a procesar: {dispo}')
        start_time = time.time()

        response = self._client.chat.completions.create(
            model="gpt-4-turbo",
            temperature=0,
            messages=[
                {"role": "system", "content": self._prompt},
                {"role": "user", "content": dispo}
            ],
            tools=self.tool_definitions,
            tool_choice={"type": "function", "function": {"name": "parse_stock_lines"}}
        )
        end_time = time.time()
        laps_time = end_time - start_time
        loggin_event(f'Respuesta recibida de OpenAI API {laps_time}')

        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            payload = tool_call.function.arguments
            loggin_event(f'Payload recibido: {payload}')
            
            parsed = json.loads(payload)
            loggin_event(f'JSON parseado: {parsed}')
            loggin_event(f'Tipo de JSON parseado: {type(parsed)}')
            
            # Verificar que es un diccionario y contiene items
            if not isinstance(parsed, dict) or "items" not in parsed:
                raise Exception(f"Se esperaba un diccionario con 'items', pero se recibió: {parsed}")
            
            items = parsed["items"]
            if not isinstance(items, list):
                raise Exception(f"Se esperaba una lista de items, pero se recibió: {type(items)}")
            
            result_arrays = []
            for item in items:
                # Validar campos requeridos para cada item
                required_fields = ["cantidad", "modelo", "tallos_totales", "precio_tallo_caja", "variedad", "medidas", "precios"]
                for field in required_fields:
                    if field not in item:
                        raise Exception(f"Campo requerido '{field}' no encontrado en item: {item}")
                
                result_array = [
                    item["cantidad"],
                    item["modelo"],
                    item["tallos_totales"],
                    item["precio_tallo_caja"],
                    item["variedad"],
                    item["medidas"],
                    item["precios"]
                ]
                result_arrays.append(result_array)
            
            loggin_event(f'Arrays resultado: {result_arrays}')
            loggin_event(f'Número de items procesados: {len(result_arrays)}')
            return result_arrays
        else:
            raise Exception("No se recibió un JSON válido desde la función")
