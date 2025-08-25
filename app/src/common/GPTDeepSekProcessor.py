import os
import time
import json
from openai import OpenAI
from common.secrets import DEEP_SEK_API_KEY
from common.AppLoger import loggin_event
from common.TextPrepare import TextPrepare


class GPTDeepSekProcessor:
    """Procesador para DeepSeek que replica el comportamiento de GPTDirectProcessor.

    Intenta usar el cliente OpenAI-compatible apuntando al endpoint de DeepSeek.
    Como la compatibilidad de function calling puede variar, se implementa un
    fallback que intenta extraer el JSON de la respuesta normal del asistente.
    """

    _api_key = DEEP_SEK_API_KEY
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _prompt = None
    _client = None
    # Permite override por ENV
    _model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    @property
    def client(self):
        if self._client is None:
            # DeepSeek es OpenAI-compatible; configuramos base_url
            os.environ.setdefault("DEEPSEEK_API_KEY", self._api_key)
            # Algunos SDK esperan OPENAI_API_KEY; duplicamos para seguridad
            os.environ.setdefault("OPENAI_API_KEY", self._api_key)
            self._client = OpenAI(
                api_key=self._api_key,
                base_url=os.getenv("DEEPSEEK_BASE_URL",
                                   "https://api.deepseek.com")
            )
        return self._client

    def process_text(self, dispo, partner=None):
        dispo = TextPrepare().process(dispo)

        if not self._prompt:
            self._load_prompt(partner)

        loggin_event('Iniciando procesamiento DeepSeek')
        start_time = time.time()

        # Intento con function calling (puede no estar soportado: manejamos excepción)
        response = None
        tool_mode_used = False
        try:
            response = self.client.chat.completions.create(
                model=self._model,
                temperature=1,
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
            tool_mode_used = True
        except Exception as e:  # noqa: BLE001
            # Fallback sin tools
            loggin_event(
                f"Fallo function calling DeepSeek, usando modo texto: {e}")
            response = self.client.chat.completions.create(
                model=self._model,
                temperature=1,
                messages=[
                    {"role": "system", "content": self._prompt +
                        "\nDevuelve solo JSON válido con la estructura pedida."},
                    {"role": "user", "content": dispo}
                ]
            )

        laps_time = time.time() - start_time
        loggin_event(f'Respuesta recibida de DeepSeek {laps_time}s')

        parsed = None
        if tool_mode_used and response.choices and response.choices[0].message.tool_calls:
            try:
                tool_call = response.choices[0].message.tool_calls[0]
                parsed = json.loads(tool_call.function.arguments)
            except Exception as e:  # noqa: BLE001
                loggin_event(
                    f"Error parseando tool_call, intentando extraer JSON del contenido: {e}")

        if parsed is None:
            # Extraer JSON del contenido libre
            content = response.choices[0].message.content if response.choices else ''
            json_str = self._extract_json(content)
            if not json_str:
                raise Exception(
                    'No se pudo extraer JSON de la respuesta de DeepSeek')
            parsed = json.loads(json_str)

        if not isinstance(parsed, dict) or "items" not in parsed:
            raise Exception(
                "Formato inválido: se esperaba diccionario con 'items'")

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

        loggin_event(f'Procesados {len(result_arrays)} items (DeepSeek)')
        return result_arrays

    def _load_prompt(self, partner=None):
        if partner and hasattr(partner, 'prompt_disponibility') and partner.prompt_disponibility:
            self._prompt = partner.prompt_disponibility.strip()
            loggin_event('Prompt DeepSeek cargado de partner')
            return
        promt_file = os.path.join(self._current_dir, 'PromtText.txt')
        if not os.path.exists(promt_file):
            raise Exception(
                'No se encontró el archivo de configuración para DeepSeek')
        with open(promt_file, 'r', encoding='utf-8') as f:
            self._prompt = f.read()
        loggin_event('Archivo de configuración DeepSeek leído correctamente')

    @staticmethod
    def _extract_json(text):
        """Intenta localizar el primer bloque JSON válido en el texto."""
        if not text:
            return None
        start = text.find('{')
        end = text.rfind('}')
        if start == -1 or end == -1 or end <= start:
            return None
        candidate = text[start:end+1]
        # Intento directo
        try:
            json.loads(candidate)
            return candidate
        except Exception:  # noqa: BLE001
            pass
        # Limpieza básica de posibles explicaciones alrededor
        # Estrategia simple: buscar cierre balanceado
        balance = 0
        for i, ch in enumerate(text):
            if ch == '{':
                if balance == 0:
                    start = i
                balance += 1
            elif ch == '}':
                balance -= 1
                if balance == 0:
                    fragment = text[start:i+1]
                    try:
                        json.loads(fragment)
                        return fragment
                    except Exception:  # noqa: BLE001
                        continue
        return None
