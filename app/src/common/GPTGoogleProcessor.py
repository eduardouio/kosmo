from common.secrets import GOOGLE_API_KEY
from google import genai
from typing import List, Dict, Optional
import json
import time
import os
import re
from common.AppLoger import loggin_event
from common.TextPrepare import TextPrepare


class GPTGoogleProcessor:
    def __init__(self, model_name: str = None):
        genai.configure(api_key=GOOGLE_API_KEY)

        if model_name:
            available_models = [model_name]
        else:
            available_models = [
                "gemini-1.5-flash-latest",
                "gemini-1.5-flash",
                "gemini-1.5-pro-latest",
                "gemini-1.5-pro",
                "gemini-1.0-pro-latest",
                "gemini-1.0-pro",
                "gemini-pro"
            ]

        self.model = None
        self.model_name = None

        for model in available_models:
            try:
                test_model = genai.GenerativeModel(model)
                test_response = test_model.generate_content(
                    "Test",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=10,
                    )
                )

                if test_response and test_response.text:
                    self.model = test_model
                    self.model_name = model
                    loggin_event(
                        f'Inicializado exitosamente con modelo: {model}'
                    )
                    break

            except Exception as e:
                loggin_event(f'Modelo {model} no disponible: {str(e)}')
                continue

        if not self.model:
            try:
                models = genai.list_models()
                for model_info in models:
                    methods = model_info.supported_generation_methods
                    if 'generateContent' in methods:
                        try:
                            self.model = genai.GenerativeModel(model_info.name)
                            self.model_name = model_info.name
                            loggin_event(
                                f'Usando modelo disponible: {model_info.name}'
                            )
                            break
                        except Exception:
                            continue
            except Exception as e:
                loggin_event(f'Error al listar modelos: {str(e)}')

        if not self.model:
            raise Exception(
                "No se pudo inicializar ningún modelo de Gemini disponible"
            )

        self.chat_session = None
        self._current_dir = os.path.dirname(os.path.abspath(__file__))
        self._prompt = None

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

        # Función que simula la herramienta parse_stock_lines
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
                                "cantidad": genai.protos.Schema(type=genai.protos.Type.INTEGER),
                                "modelo": genai.protos.Schema(type=genai.protos.Type.STRING),
                                "variedades": genai.protos.Schema(
                                    type=genai.protos.Type.ARRAY,
                                    items=genai.protos.Schema(
                                        type=genai.protos.Type.STRING)
                                ),
                                "medidas": genai.protos.Schema(
                                    type=genai.protos.Type.ARRAY,
                                    items=genai.protos.Schema(
                                        type=genai.protos.Type.INTEGER)
                                ),
                                "tallos": genai.protos.Schema(
                                    type=genai.protos.Type.ARRAY,
                                    items=genai.protos.Schema(
                                        type=genai.protos.Type.INTEGER)
                                ),
                                "precios": genai.protos.Schema(
                                    type=genai.protos.Type.ARRAY,
                                    items=genai.protos.Schema(
                                        type=genai.protos.Type.NUMBER)
                                )
                            },
                            required=["cantidad", "modelo", "variedades",
                                "medidas", "tallos", "precios"]
                        )
                    )
                },
                required=["items"]
            )
        )

        tool = genai.protos.Tool(function_declarations=[function_declaration])

        try:
            response = self.model.generate_content(
                [self._prompt, dispo],
                tools=[tool],
                tool_config=genai.protos.ToolConfig(
                    function_calling_config=genai.protos.ToolConfig.FunctionCallingConfig(
                        mode=genai.protos.ToolConfig.FunctionCallingConfig.Mode.ANY,
                        allowed_function_names=["parse_stock_lines"]
                    )
                ),
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    max_output_tokens=8192
                )
            )

            end_time = time.time()
            laps_time = end_time - start_time
            loggin_event(
                f'Respuesta recibida de Google Gemini API {laps_time}')

            # Verificar si hay function calls en la respuesta
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        if function_call.name == "parse_stock_lines":
                            # Extraer argumentos de la función
                            payload = json.dumps(dict(function_call.args))
                            loggin_event(f'Payload recibido: {payload}')

                            parsed = json.loads(payload)
                            loggin_event(f'JSON parseado: {parsed}')
                            loggin_event(
                                f'Tipo de JSON parseado: {type(parsed)}')

                            # Verificar que es un diccionario y contiene items
                            if not isinstance(parsed, dict) or "items" not in parsed:
                                raise Exception(
                                    f"Se esperaba un diccionario con 'items', pero se recibió: {parsed}")

                            items = parsed["items"]
                            if not isinstance(items, list):
                                raise Exception(
                                    f"Se esperaba una lista de items, pero se recibió: {type(items)}")

                            result_arrays = []
                            for item in items:
                                # Validar campos requeridos para cada item
                                required_fields = [
                                    "cantidad", "modelo", "variedades", "medidas", "tallos", "precios"]
                                for field in required_fields:
                                    if field not in item:
                                        raise Exception(
                                            f"Campo requerido '{field}' no encontrado en item: {item}")

                                result_array = [
                                    item["cantidad"],
                                    item["modelo"],
                                    item["variedades"],
                                    item["medidas"],
                                    item["tallos"],
                                    item["precios"]
                                ]
                                result_arrays.append(result_array)

                            loggin_event(f'Arrays resultado: {result_arrays}')
                            loggin_event(
                                f'Número de items procesados: {len(result_arrays)}')
                            return result_arrays

            raise Exception("No se recibió un JSON válido desde la función")

        except Exception as e:
            loggin_event(f'Error en procesamiento con Google Gemini: {str(e)}')
            raise Exception(f"Error al procesar con Google Gemini: {str(e)}")

    def start_chat(self, history: Optional[List[Dict[str, str]]] = None):
        if history:
            gemini_history = self._convert_history_format(history)
            self.chat_session = self.model.start_chat(history=gemini_history)
        else:
            self.chat_session = self.model.start_chat()

    def process_message(
        self,
        message: str,
        system_prompt: Optional[str] = None
    ) -> str:
        try:
            if system_prompt and not self.chat_session:
                full_prompt = f"{system_prompt}\n\nUsuario: {message}"
                response = self.model.generate_content(full_prompt)
            elif self.chat_session:
                response = self.chat_session.send_message(message)
            else:
                response = self.model.generate_content(message)

            return response.text
        except Exception as e:
            return f"Error al procesar el mensaje: {str(e)}"

    def process_batch(
        self,
        messages: List[str],
        system_prompt: Optional[str] = None
    ) -> List[str]:
        responses = []
        for message in messages:
            response = self.process_message(message, system_prompt)
            responses.append(response)
        return responses

    def _convert_history_format(
        self,
        history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        gemini_history = []
        for entry in history:
            if entry.get("role") == "user":
                gemini_history.append({
                    "role": "user",
                    "parts": [entry.get("content", "")]
                })
            elif entry.get("role") == "assistant":
                gemini_history.append({
                    "role": "model",
                    "parts": [entry.get("content", "")]
                })
        return gemini_history

    def reset_chat(self):
        self.chat_session = None

    def get_available_models(self) -> List[str]:
        try:
            models = genai.list_models()
            return [
                model.name for model in models
                if 'generateContent' in model.supported_generation_methods
            ]
        except Exception as e:
            return [f"Error obteniendo modelos: {str(e)}"]
        return gemini_history

    def reset_chat(self):
        self.chat_session = None

    def get_available_models(self) -> List[str]:
        try:
            models = genai.list_models()
            return [
                model.name for model in models
                if 'generateContent' in model.supported_generation_methods
            ]
        except Exception as e:
            return [f"Error obteniendo modelos: {str(e)}"]
