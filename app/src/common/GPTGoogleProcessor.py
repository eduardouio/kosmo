from common.secrets import GOOGLE_API_KEY
from google import genai
"""Procesador Gemini con interfaz equivalente a GPTDirectProcessor."""

from common.secrets import GOOGLE_API_KEY
from google import genai
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
    _model_name = "gemini-1.5-flash"

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

        function_declaration = genai.protos.FunctionDeclaration(
            name="parse_stock_lines",
            description="Parse stock lines into structured format",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "items": genai.protos.Schema(
                        type=genai.protos.Type.ARRAY,
                        items=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "cantidad": genai.protos.Schema(
                                    type=genai.protos.Type.INTEGER),
                                "modelo": genai.protos.Schema(
                                    type=genai.protos.Type.STRING),
                                "variedades": genai.protos.Schema(
                                    type=genai.protos.Type.ARRAY,
                                    items=genai.protos.Schema(
                                        type=genai.protos.Type.STRING)
                                ),
                                "medidas": genai.protos.Schema(
                                    type=genai.protos.Type.ARRAY,
                                    items=genai.protos.Schema(
                                        type=genai.protos.Type.NUMBER)
                                ),
                                "tallos": genai.protos.Schema(
                                    type=genai.protos.Type.ARRAY,
                                    items=genai.protos.Schema(
                                        type=genai.protos.Type.NUMBER)
                                ),
                                "precios": genai.protos.Schema(
                                    type=genai.protos.Type.ARRAY,
                                    items=genai.protos.Schema(
                                        type=genai.protos.Type.NUMBER)
                                )
                            },
                            required=[
                                "cantidad", "modelo", "variedades",
                                "medidas", "tallos", "precios"
                            ]
                        )
                    )
                },
                required=["items"]
            )
        )
        tool = genai.protos.Tool(
            function_declarations=[function_declaration])

        try:
            response = self.client.generate_content(
                [self._prompt, dispo],
                tools=[tool],
                tool_config=genai.protos.ToolConfig(
                    function_calling_config=genai.protos.ToolConfig.
                    FunctionCallingConfig(
                        mode=genai.protos.ToolConfig.FunctionCallingConfig.
                        Mode.ALWAYS,
                        allowed_function_names=["parse_stock_lines"]
                    )
                ),
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    max_output_tokens=4096
                )
            )

            laps_time = time.time() - start_time
            loggin_event(
                f'Respuesta recibida de Google Gemini API {laps_time}s')

            if (not response.candidates or
                    not response.candidates[0].content.parts):
                raise Exception(
                    "No se recibió una respuesta válida desde Gemini")

            parsed = None
            for part in response.candidates[0].content.parts:
                fc = getattr(part, 'function_call', None)
                if fc and fc.name == "parse_stock_lines":
                    raw_args = fc.args
                    if isinstance(raw_args, dict):
                        parsed = raw_args
                    else:
                        # Fallbacks
                        for extractor in (
                            getattr(raw_args, 'to_dict', None), None
                        ):
                            if callable(extractor):
                                try:
                                    parsed = extractor()
                                    break
                                except Exception:
                                    pass
                        if parsed is None:
                            try:
                                parsed = json.loads(str(raw_args))
                            except Exception:
                                parsed = None
                    break

            if parsed is None:
                raise Exception(
                    "No se recibió un JSON válido desde la función")

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
        loggin_event('Archivo de configuración leído correctamente')
