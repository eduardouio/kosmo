import pytest
from common import GPTGoogleProcessor, TextPrepare
from common.AppLoger import loggin_event
import os
import re
import ast
from unittest.mock import patch, MagicMock
import json

# Ruta al archivo PromtText.txt
_PROMPT_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', 'common', 'PromtText.txt'
)

def load_test_cases():
    """
    Carga casos de prueba desde el archivo PromtText.txt.
    Extrae entradas y salidas esperadas de las secciones de ejemplos.
    """
    test_cases = []

    if not os.path.exists(_PROMPT_FILE_PATH):
        return test_cases

    with open(_PROMPT_FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Parsear "Ejemplos de interpretación"
    example_section_match = re.search(
        r"Ejemplos de interpretación para cada entrada que puede venir:(.*?)(?=\n\n|\Z)",
        content, re.DOTALL
    )

    if example_section_match:
        example_text = example_section_match.group(1)
        # Buscar patrones ENTRADA: ... SALIDA: ...
        pattern = r"ENTRADA:\s*(.*?)\s*SALIDA:\s*(.*?)(?=\n\s*ENTRADA:|\Z)"
        matches = re.findall(pattern, example_text, re.DOTALL)

        for input_str, output_str in matches:
            input_str = input_str.strip()
            output_str = output_str.strip()

            if input_str and output_str:
                try:
                    expected_output = [ast.literal_eval(output_str)]
                    test_id = f"ejemplo_{input_str[:30].replace(' ', '_')}"
                    test_cases.append(pytest.param(
                        input_str, expected_output, id=test_id))
                except Exception as e:
                    print(
                        f"Error parseando ejemplo: {input_str[:50]}... - {e}")

    # 2. Parsear casos especiales "DISPONIBILIDAD DIFERENTE"
    special_cases = [
        (r"DISPONIBILIDAD DIFERENTE:\s*\n(.*?)\n.*?La salida de este caso especial debe ser:\s*\n(.*?)(?=\n\n|\n[A-Z]|\Z)", "especial"),
        (r"Variacion del caso anterior\s*\n(.*?)\n.*?La salida de este caso especial debe ser:\s*\n(.*?)(?=\n\n|\n[A-Z]|\Z)", "variacion")
    ]

    for pattern, prefix in special_cases:
        matches = re.findall(pattern, content, re.DOTALL)
        for input_block, output_str in matches:
            input_str = input_block.strip().split('\n')[0].strip()
            output_str = output_str.strip()

            if input_str and output_str:
                try:
                    expected_output = [ast.literal_eval(output_str)]
                    test_id = f"{prefix}_{input_str[:30].replace(' ', '_')}"
                    test_cases.append(pytest.param(
                        input_str, expected_output, id=test_id))
                except Exception as e:
                    print(
                        f"Error parseando {prefix}: {input_str[:50]}... - {e}")

    return test_cases

@pytest.mark.django_db
class TestGPTGoogleProcessor:

    # Cargar casos de prueba
    test_data = load_test_cases()

    def setup_method(self):
        """Setup method que maneja la inicialización con mocks si es necesario."""
        loggin_event('[TEST] Inicializando GPTGoogleProcessor')
        self.text_normalizer = TextPrepare()
        
        # Intentar inicializar sin mock primero, si falla usar mock
        try:
            # Mock de la configuración inicial para evitar llamadas reales
            with patch('common.GPTGoogleProcessor.genai.configure'):
                with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                    # Configurar mock exitoso
                    mock_model = MagicMock()
                    mock_response = MagicMock()
                    mock_response.text = "test response"
                    mock_model.generate_content.return_value = mock_response
                    mock_model_class.return_value = mock_model
                    
                    self.gpt_google_processor = GPTGoogleProcessor()
                    
        except Exception as e:
            pytest.skip(f"No se pudo inicializar GPTGoogleProcessor: {e}")

    def test_init_processor_with_mock(self):
        """Test de inicialización básica del procesador con mock."""
        with patch('common.GPTGoogleProcessor.genai.configure'):
            with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = "test response"
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                processor = GPTGoogleProcessor()
                assert processor is not None
                assert processor.model is not None
                assert processor._prompt is None

    def test_load_prompt_success(self):
        """Test de carga exitosa del archivo de prompt."""
        with patch('common.GPTGoogleProcessor.genai.configure'):
            with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = "test"
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                processor = GPTGoogleProcessor()
                
                # Cargar prompt manualmente para el test
                promt_file = os.path.join(processor._current_dir, 'PromtText.txt')
                if os.path.exists(promt_file):
                    with open(promt_file, 'r', encoding='utf-8') as file:
                        processor._prompt = file.read()
                
                assert processor._prompt is not None
                assert len(processor._prompt) > 0
                assert "comercializador de flores" in processor._prompt.lower()

    def test_load_prompt_file_not_found(self, monkeypatch):
        """Test de manejo de error cuando no se encuentra el archivo de prompt."""
        with patch('common.GPTGoogleProcessor.genai.configure'):
            with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = "test"
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                processor = GPTGoogleProcessor()

                # Mock os.path.exists para simular archivo no encontrado
                def mock_exists(path):
                    if 'PromtText.txt' in path:
                        return False
                    return True

                monkeypatch.setattr(os.path, 'exists', mock_exists)

                with pytest.raises(Exception) as excinfo:
                    processor.process_text("test input")
                assert "No se encontró el archivo de configuración" in str(excinfo.value)

    @pytest.mark.parametrize("input_text, expected_output", test_data if test_data else [])
    def test_process_text_with_examples_mock(self, input_text, expected_output):
        """
        Test del procesamiento de texto con ejemplos del prompt usando mock.
        """
        with patch('common.GPTGoogleProcessor.genai.configure'):
            with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                
                # Mock de la respuesta esperada basada en expected_output
                mock_candidate = MagicMock()
                mock_part = MagicMock()
                mock_function_call = MagicMock()
                
                if expected_output:
                    expected_item = expected_output[0]  # Primer item esperado
                    mock_response_data = {
                        "items": [{
                            "cantidad": expected_item[0],
                            "modelo": expected_item[1],
                            "variedades": expected_item[2],
                            "medidas": expected_item[3],
                            "tallos": expected_item[4],
                            "precios": expected_item[5]
                        }]
                    }
                    mock_function_call.name = "parse_stock_lines"
                    mock_function_call.args = mock_response_data
                else:
                    mock_function_call.name = "parse_stock_lines"
                    mock_function_call.args = {"items": []}
                    
                mock_part.function_call = mock_function_call
                mock_candidate.content.parts = [mock_part]
                
                mock_response = MagicMock()
                mock_response.candidates = [mock_candidate]
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model

                processor = GPTGoogleProcessor()

                try:
                    result = processor.process_text(input_text)

                    # Verificar estructura básica
                    assert isinstance(result, list)
                    
                    if expected_output:
                        assert len(result) > 0
                        
                        # Verificar formato de cada item
                        for item in result:
                            assert isinstance(item, list)
                            # [cantidad, modelo, variedades, medidas, tallos, precios]
                            assert len(item) == 6
                            assert isinstance(item[0], int)  # cantidad
                            assert isinstance(item[1], str)  # modelo
                            assert isinstance(item[2], list)  # variedades
                            assert isinstance(item[3], list)  # medidas
                            assert isinstance(item[4], list)  # tallos
                            assert isinstance(item[5], list)  # precios

                        # Comparar con resultado esperado
                        assert result == expected_output, f"Para '{input_text}', esperado {expected_output}, obtenido {result}"

                except Exception as e:
                    pytest.fail(f"Error procesando '{input_text}': {e}")

    def test_process_simple_case_with_mock(self):
        """Test con un caso simple conocido usando mock."""
        with patch('common.GPTGoogleProcessor.genai.configure'):
            with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                
                # Mock respuesta para caso simple
                mock_candidate = MagicMock()
                mock_part = MagicMock()
                mock_function_call = MagicMock()
                
                mock_response_data = {
                    "items": [{
                        "cantidad": 2,
                        "modelo": "HB",
                        "variedades": ["EXPLORER"],
                        "medidas": [60],
                        "tallos": [350],
                        "precios": [0.30]
                    }]
                }
                
                mock_function_call.name = "parse_stock_lines"
                mock_function_call.args = mock_response_data
                mock_part.function_call = mock_function_call
                mock_candidate.content.parts = [mock_part]
                
                mock_response = MagicMock()
                mock_response.candidates = [mock_candidate]
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model

                processor = GPTGoogleProcessor()

                input_text = "2hb Explorer 60 x 350 0,30"
                result = processor.process_text(input_text)

                assert len(result) == 1
                item = result[0]
                assert item[0] == 2  # cantidad
                assert item[1] == "HB"  # modelo
                assert "EXPLORER" in item[2]  # variedad
                assert 60 in item[3]  # medida
                assert 350 in item[4]  # tallos
                assert 0.30 in item[5]  # precio

    def test_process_empty_input(self):
        """Test con entrada vacía."""
        with patch('common.GPTGoogleProcessor.genai.configure'):
            with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                
                # Mock de respuesta para entrada vacía
                mock_response = MagicMock()
                mock_response.candidates = []
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model

                processor = GPTGoogleProcessor()

                with pytest.raises(Exception) as excinfo:
                    processor.process_text("")
                assert "No se recibió un JSON válido" in str(excinfo.value)

    def test_process_invalid_response_format(self):
        """Test con respuesta inválida de la API."""
        with patch('common.GPTGoogleProcessor.genai.configure'):
            with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                
                # Mock de respuesta con formato inválido
                mock_candidate = MagicMock()
                mock_part = MagicMock()
                mock_function_call = MagicMock()
                
                mock_function_call.name = "parse_stock_lines"
                mock_function_call.args = {"invalid": "format"}
                mock_part.function_call = mock_function_call
                mock_candidate.content.parts = [mock_part]
                
                mock_response = MagicMock()
                mock_response.candidates = [mock_candidate]
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model

                processor = GPTGoogleProcessor()

                with pytest.raises(Exception) as excinfo:
                    processor.process_text("test input")
                assert "Se esperaba un diccionario con 'items'" in str(excinfo.value)

    @pytest.mark.skipif(test_data == [], reason="No hay datos de prueba cargados")
    def test_test_data_loaded(self):
        """Verificar que se cargaron datos de prueba."""
        assert len(self.test_data) > 0
        print(f"Cargados {len(self.test_data)} casos de prueba")

    def test_text_prepare_integration(self):
        """Test de integración con TextPrepare."""
        with patch('common.GPTGoogleProcessor.genai.configure'):
            with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                
                mock_candidate = MagicMock()
                mock_part = MagicMock()
                mock_function_call = MagicMock()
                
                mock_function_call.name = "parse_stock_lines"
                mock_function_call.args = {"items": []}
                mock_part.function_call = mock_function_call
                mock_candidate.content.parts = [mock_part]
                
                mock_response = MagicMock()
                mock_response.candidates = [mock_candidate]
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model

                processor = GPTGoogleProcessor()

                # Mock TextPrepare correctamente en el lugar donde se usa
                with patch('common.GPTGoogleProcessor.TextPrepare') as mock_text_prepare_class:
                    mock_text_prepare_instance = MagicMock()
                    mock_text_prepare_instance.process.return_value = "processed text"
                    mock_text_prepare_class.return_value = mock_text_prepare_instance

                    result = processor.process_text("raw text")

                    # Verificar que TextPrepare se instanció y se llamó process
                    mock_text_prepare_class.assert_called_once()
                    mock_text_prepare_instance.process.assert_called_once_with("raw text")

    # Tests que requieren llamadas reales a la API de Google (solo si está disponible)
    @pytest.mark.skipif(not os.getenv('GOOGLE_API_KEY'), reason="Google API key no configurada")
    def test_google_gemini_real_api_basic(self):
        """Test con llamada real a la API de Google Gemini para verificar conectividad básica."""
        try:
            processor = GPTGoogleProcessor()
            
            # Test simple
            simple_input = "1hb Rosa Roja 60 x 200 0,50"
            
            response = processor.process_text(simple_input)
            
            assert isinstance(response, list)
            if response:  # Solo verificar estructura si hay respuesta
                assert len(response) >= 1
                
                item = response[0]
                assert len(item) == 6
                assert isinstance(item[0], int)  # cantidad
                assert isinstance(item[1], str)  # modelo
                assert isinstance(item[2], list)  # variedades
                assert isinstance(item[3], list)  # medidas
                assert isinstance(item[4], list)  # tallos
                assert isinstance(item[5], list)  # precios
                
        except Exception as e:
            if "not found" in str(e) or "404" in str(e) or "API_KEY" in str(e):
                pytest.skip(f"API no disponible o configurada: {e}")
            else:
                raise

    def test_error_handling(self):
        """Test para verificar el manejo de errores."""
        with patch('common.GPTGoogleProcessor.genai.configure'):
            with patch('common.GPTGoogleProcessor.genai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                
                # Mock que simula error en la API
                mock_model.generate_content.side_effect = Exception("API Error")
                mock_model_class.return_value = mock_model

                processor = GPTGoogleProcessor()

                with pytest.raises(Exception) as excinfo:
                    processor.process_text("test input")
                assert "Error al procesar con Google Gemini" in str(excinfo.value)

        loggin_event('[TEST] Test de manejo de errores completado')
        response = self.gpt_google_processor.process_text(combined_text)

        # Validaciones generales
        assert isinstance(response, list)
        assert len(response) == len(test_entries)

        # Validar estructura de cada respuesta
        for i, item in enumerate(response):
            loggin_event(f'[TEST] Validando item {i}: {item}')

            # Cada item debe ser una lista con 6 elementos
            assert isinstance(item, list)
            assert len(item) == 6

            # Validar tipos básicos
            cantidad, modelo, variedades, medidas, tallos, precios = item

            # Cantidad debe ser entero positivo
            assert isinstance(cantidad, int)
            assert cantidad > 0

            # Modelo debe ser string y uno de los valores válidos
            assert isinstance(modelo, str)
            assert modelo.upper() in ["HB", "QB", "EB", "FB"]

            # Variedades debe ser lista de strings
            assert isinstance(variedades, list)
            assert all(isinstance(v, str) for v in variedades)
            assert len(variedades) > 0

            # Medidas debe ser lista de enteros
            assert isinstance(medidas, list)
            assert all(isinstance(m, (int, float)) for m in medidas)

            # Tallos debe ser lista de enteros
            assert isinstance(tallos, list)
            assert all(isinstance(t, (int, float)) for t in tallos)

            # Precios debe ser lista de números
            assert isinstance(precios, list)
            assert all(isinstance(p, (int, float)) for p in precios)

            # Las listas de variedades, medidas, tallos y precios deben tener la misma longitud
            assert len(variedades) == len(
                medidas) == len(tallos) == len(precios)

        # Validaciones específicas para algunas entradas conocidas
        # Primer item: "1hb Country Blues 50/60 x 300 0,35/0,40"
        first_item = response[0]
        assert first_item[0] == 1  # cantidad
        assert first_item[1].upper() == "HB"  # modelo
        assert "COUNTRY BLUES" in [v.upper()
                                   for v in first_item[2]]  # variedad
        assert 50 in first_item[3] and 60 in first_item[3]  # medidas

        # Item con CANDY XPRESSION: verificar corrección de nombre
        candy_items = [item for item in response if any(
            "CANDY" in str(v).upper() for v in item[2])]
        assert len(candy_items) >= 2
        for candy_item in candy_items:
            assert any("CANDY XPRESSION" in str(v).upper()
                       for v in candy_item[2])

        loggin_event(
            f'[TEST] Test de entradas específicas completado exitosamente con Google Gemini. Procesados {len(response)} items')

    def test_literal_output_validation(self):
        """Test que valida las salidas de forma literal contra valores esperados usando Google Gemini"""
        loggin_event(
            '[TEST] Iniciando test de validación literal de salidas con Google Gemini')

        # Casos de test con entradas y salidas esperadas
        test_cases = [
            {
                "input": "1hb Country Blues 50/60 x 300 0,35/0,40",
                "expected": [1, "HB", ["COUNTRY BLUES", "COUNTRY BLUES"], [50, 60], [300, 0], [0.35, 0.40]]
            },
            {
                "input": "1qb Playa Blanca 70 x 100 0,75",
                "expected": [1, "QB", ["PLAYA BLANCA"], [70], [100], [0.75]]
            },
            {
                "input": "1hb Priceless 50 x 400 0,30",
                "expected": [1, "HB", ["PRICELESS"], [50], [400], [0.30]]
            },
            {
                "input": "2hb Explorer 60 x 350 0,30",
                "expected": [2, "HB", ["EXPLORER"], [60], [350], [0.30]]
            },
            {
                "input": "2hb Freedom 50 x 450 0,24",
                "expected": [2, "HB", ["FREEDOM"], [50], [450], [0.24]]
            }
        ]

        for i, test_case in enumerate(test_cases):
            loggin_event(
                f'[TEST] Procesando caso {i+1} con Google Gemini: {test_case["input"]}')

            # Procesar entrada individual
            response = self.gpt_google_processor.process_text(
                test_case["input"])

            # Validar que se devuelve exactamente un item
            assert len(
                response) == 1, f"Se esperaba 1 item, se obtuvo {len(response)}"

            actual = response[0]
            expected = test_case["expected"]

            # Validar estructura general
            assert len(
                actual) == 6, f"Se esperaban 6 elementos, se obtuvieron {len(actual)}"
            assert len(
                expected) == 6, f"Formato de test incorrecto: se esperaban 6 elementos en expected"

            # Validar cada campo individualmente
            assert actual[0] == expected[0], f"Cantidad: esperado {expected[0]}, obtenido {actual[0]}"
            assert actual[1].upper() == expected[1].upper(
            ), f"Modelo: esperado {expected[1]}, obtenido {actual[1]}"

            # Validar variedades (normalizar a mayúsculas para comparación)
            actual_variedades = [v.upper() for v in actual[2]]
            expected_variedades = [v.upper() for v in expected[2]]
            assert actual_variedades == expected_variedades, f"Variedades: esperado {expected_variedades}, obtenido {actual_variedades}"

            # Validar medidas
            assert actual[3] == expected[3], f"Medidas: esperado {expected[3]}, obtenido {actual[3]}"

            # Validar tallos
            assert actual[4] == expected[4], f"Tallos: esperado {expected[4]}, obtenido {actual[4]}"

            # Validar precios (con tolerancia para decimales)
            for j, (actual_price, expected_price) in enumerate(zip(actual[5], expected[5])):
                assert abs(
                    actual_price - expected_price) < 0.001, f"Precio {j}: esperado {expected_price}, obtenido {actual_price}"

            loggin_event(
                f'[TEST] Caso {i+1} validado exitosamente con Google Gemini')

        loggin_event(
            f'[TEST] Validación literal completada exitosamente con Google Gemini. {len(test_cases)} casos procesados')

    def test_google_gemini_basic_functionality(self):
        """Test específico para verificar la funcionalidad básica de Google Gemini"""
        loggin_event('[TEST] Iniciando test de funcionalidad básica de Google Gemini')

        # Test simple
        simple_input = "1hb Rosa Roja 60 x 200 0,50"
        
        try:
            response = self.gpt_google_processor.process_text(simple_input)
        except Exception as e:
            if "not found" in str(e) or "404" in str(e):
                pytest.skip(f"Modelo no disponible: {e}")
            else:
                raise

        assert isinstance(response, list)
        assert len(response) == 1
        
        item = response[0]
        assert len(item) == 6
        assert item[0] == 1  # cantidad
        assert item[1].upper() == "HB"  # modelo
        assert isinstance(item[2], list)  # variedades
        assert isinstance(item[3], list)  # medidas
        assert isinstance(item[4], list)  # tallos
        assert isinstance(item[5], list)  # precios

        loggin_event('[TEST] Test de funcionalidad básica de Google Gemini completado exitosamente')

    def test_error_handling(self):
        """Test para verificar el manejo de errores"""
        loggin_event(
            '[TEST] Iniciando test de manejo de errores con Google Gemini')

        # Test con entrada vacía
        try:
            response = self.gpt_google_processor.process_text("")
            # Si no falla, debería devolver lista vacía o lanzar excepción controlada
            assert isinstance(response, list)
        except Exception as e:
            # Se espera que falle de forma controlada
            assert "Error" in str(e)

        loggin_event('[TEST] Test de manejo de errores completado')
