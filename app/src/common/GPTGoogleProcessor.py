from common.secrets import GOOGLE_API_KEY
import google.generativeai as genai
from common.AppLoger import loggin_event
from common.TextPrepare import TextPrepare
import time
import json
import os


class GPTGoogleProcessor:
    _api_key = GOOGLE_API_KEY
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _prompt = None
    _client = None
    _model_name = "gemini-2.0-flash"

    @property
    def client(self):
        if self._client is None:
            genai.configure(api_key=self._api_key)
            try:
                model = genai.GenerativeModel(self._model_name)
                # Llamada mínima para validar
                model.generate_content("ping")
                self._client = model
                loggin_event(
                    f'Modelo Gemini inicializado: {self._model_name}')
            except Exception as e:
                raise Exception(
                    f"Fallo inicializando Gemini '{self._model_name}': {e}")
        return self._client

    def process_text(self, dispo, partner=None):
        """Procesa texto de disponibilidad devolviendo lista de items.

    Retorna: [[cantidad, modelo, variedades[], medidas[], tallos[],
    precios[]], ...]
        Levanta Exception en formato inválido (igual que GPTDirectProcessor).
        """
        dispo = TextPrepare().process(dispo)

        if not self._prompt:
            self._load_prompt(partner)

        loggin_event('Iniciando procesamiento de texto')
        start_time = time.time()

    # Salida JSON directa (sin function calling) para paridad.

        json_instruction = (
            "Responde SOLO con JSON válido UTF-8 sin texto extra ni "
            "explicaciones. Estructura: {\\n  'items': [ { 'cantidad': int, "
            "'modelo': string, 'variedades': [string], 'medidas': [number], "
            "'tallos': [number], 'precios': [number] } ... ]\\n}. Usa arrays "
            "alineados por índice. No incluyas comentarios ni markdown."
        )
        full_prompt = (
            f"{self._prompt}\n\n{json_instruction}\n\nTexto:\n{dispo}"
        )

        try:
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    max_output_tokens=2048
                )
            )

            laps_time = time.time() - start_time
            loggin_event(
                f'Respuesta recibida de Google Gemini API {laps_time}s')

            if not response or not getattr(response, 'text', None):
                raise Exception("Respuesta vacía de Gemini")

            raw_text = response.text.strip()

            # Limpiar bloques markdown si existen
            if raw_text.startswith('```'):
                # posible formato ```json ... ```
                raw_text = raw_text.strip('`')
                # quitar posible json inicial
                raw_text = raw_text.replace('json\n', '', 1)
                raw_text = raw_text.replace('json\r\n', '', 1)

            # Extraer el primer objeto JSON completo
            parsed = None
            try:
                parsed = json.loads(raw_text)
            except Exception:
                # Heurística: buscar desde primer '{' hasta última '}'
                try:
                    start = raw_text.index('{')
                    end = raw_text.rindex('}') + 1
                    snippet = raw_text[start:end]
                    parsed = json.loads(snippet)
                except Exception:
                    parsed = None

            if parsed is None:
                raise Exception("No se pudo parsear JSON de Gemini")

            if (not isinstance(parsed, dict) or
                    "items" not in parsed or
                    not isinstance(parsed["items"], list)):
                raise Exception(
                    "Formato inválido: se esperaba diccionario con lista"
                    " 'items'")

            required = [
                "cantidad", "modelo", "variedades",
                "medidas", "tallos", "precios"
            ]
            result = []
            for idx, item in enumerate(parsed["items"]):
                if not isinstance(item, dict):
                    raise Exception(f"Item {idx} no es un objeto válido")
                if not all(f in item for f in required):
                    miss = [f for f in required if f not in item]
                    raise Exception(
                        f"Campos faltantes en item {idx}: {miss}")

                def _to_int(v):
                    try:
                        return int(v)
                    except Exception:
                        return v

                def _to_float(v):
                    try:
                        return float(v)
                    except Exception:
                        return v

                cantidad = _to_int(item["cantidad"])
                modelo = (item["modelo"].strip()
                          if isinstance(item["modelo"], str)
                          else item["modelo"])
                variedades = [
                    v.strip() for v in item.get("variedades", [])
                    if isinstance(v, str)
                ]
                medidas = [_to_float(m) for m in item.get("medidas", [])]
                tallos = [_to_int(t) for t in item.get("tallos", [])]
                precios = [_to_float(p) for p in item.get("precios", [])]

                result.append([
                    cantidad, modelo, variedades, medidas, tallos, precios
                ])

            loggin_event(f'Procesados {len(result)} items')
            return result

        except Exception as e:
            loggin_event(
                f'Error en procesamiento con Google Gemini: {str(e)}')
            raise Exception(
                f"Error al procesar con Google Gemini: {str(e)}")

    def _load_prompt(self, partner=None):
        if (partner and hasattr(partner, 'prompt_disponibility') and
                partner.prompt_disponibility):
            self._prompt = partner.prompt_disponibility.strip()
            loggin_event(
                'Prompt cargado desde prompt_disponibility del partner')
            return

        promt_file = os.path.join(self._current_dir, 'PromtText.txt')
        if not os.path.exists(promt_file):
            raise Exception('No se encontró el archivo de configuración')

        with open(promt_file, 'r', encoding='utf-8') as file:
            self._prompt = file.read()
    loggin_event('Archivo de configuración leído correctamente')
