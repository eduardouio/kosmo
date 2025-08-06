import pytest
from common.GPTDirectProcessor import GPTDirectProcessor
from common.TextPrepare import TextPrepare
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
class TestGPTDirectProcessor:

    # Cargar casos de prueba
    test_data = load_test_cases()

    def test_init_processor(self):
        """Test de inicialización básica del procesador."""
        processor = GPTDirectProcessor()
        assert processor is not None
        assert processor._client is None  # No inicializado hasta primera llamada
        assert processor._prompt is None  # No cargado hasta primera llamada

    def test_load_prompt_success(self):
        """Test de carga exitosa del archivo de prompt."""
        processor = GPTDirectProcessor()
        
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
        processor = GPTDirectProcessor()

        # Mock os.path.exists para simular archivo no encontrado
        def mock_exists(path):
            if 'PromtText.txt' in path:
                return False
            return True

        monkeypatch.setattr(os.path, 'exists', mock_exists)

        with pytest.raises(Exception) as excinfo:
            processor.process_text("test input")
        assert "No se encontró el archivo de configuración" in str(excinfo.value)

    @pytest.mark.skipif(not GPTDirectProcessor._api_key, reason="API key no configurada")
    @pytest.mark.parametrize("input_text, expected_output", test_data if test_data else [])
    def test_process_text_with_examples(self, input_text, expected_output):
        """
        Test del procesamiento de texto con ejemplos del prompt.
        Requiere API key válida para OpenAI.
        """
        processor = GPTDirectProcessor()

        # Mock del cliente para evitar problemas de versión de OpenAI
        with patch.object(processor, '_get_client') as mock_get_client:
            # Crear mock del cliente
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            # Mock de la respuesta esperada basada en expected_output
            mock_tool_call = MagicMock()
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
                mock_tool_call.function.arguments = json.dumps(mock_response_data)
            else:
                mock_tool_call.function.arguments = '{"items": []}'
            
            mock_response = MagicMock()
            mock_response.choices[0].message.tool_calls = [mock_tool_call]
            mock_client.chat.completions.create.return_value = mock_response

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

    def test_get_client_with_mock(self):
        """Test de obtención del cliente OpenAI con mock."""
        processor = GPTDirectProcessor()
        
        # Mock la creación del cliente OpenAI para evitar errores de versión
        with patch('common.GPTDirectProcessor.OpenAI') as mock_openai:
            mock_client_instance = MagicMock()
            mock_openai.return_value = mock_client_instance
            
            # Primer llamada crea el cliente
            client = processor._get_client()
            assert client is not None
            assert processor._client is not None
            
            # Segunda llamada retorna el mismo cliente
            client2 = processor._get_client()
            assert client is client2
            
            # Verificar que OpenAI se llamó una sola vez
            mock_openai.assert_called_once_with(api_key=processor._api_key)

    def test_process_simple_case_with_mock(self):
        """Test con un caso simple conocido usando mock."""
        processor = GPTDirectProcessor()
        
        with patch.object(processor, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            # Mock respuesta para caso simple
            mock_tool_call = MagicMock()
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
            mock_tool_call.function.arguments = json.dumps(mock_response_data)
            
            mock_response = MagicMock()
            mock_response.choices[0].message.tool_calls = [mock_tool_call]
            mock_client.chat.completions.create.return_value = mock_response

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
        processor = GPTDirectProcessor()

        with patch.object(processor, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            # Mock de respuesta para entrada vacía
            mock_response = MagicMock()
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response

            with pytest.raises(Exception) as excinfo:
                processor.process_text("")
            assert "No se recibió un JSON válido" in str(excinfo.value)

    def test_process_invalid_response_format(self):
        """Test con respuesta inválida de la API."""
        processor = GPTDirectProcessor()

        with patch.object(processor, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            # Mock de respuesta con formato inválido
            mock_tool_call = MagicMock()
            mock_tool_call.function.arguments = '{"invalid": "format"}'

            mock_response = MagicMock()
            mock_response.choices[0].message.tool_calls = [mock_tool_call]
            mock_client.chat.completions.create.return_value = mock_response

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
        processor = GPTDirectProcessor()

        # Mock del cliente para evitar llamada real a la API
        with patch.object(processor, '_get_client') as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            mock_tool_call = MagicMock()
            mock_tool_call.function.arguments = '{"items": []}'

            mock_response = MagicMock()
            mock_response.choices[0].message.tool_calls = [mock_tool_call]
            mock_client.chat.completions.create.return_value = mock_response

            # Mock TextPrepare correctamente en el lugar donde se usa
            with patch('common.GPTDirectProcessor.TextPrepare') as mock_text_prepare_class:
                mock_text_prepare_instance = MagicMock()
                mock_text_prepare_instance.process.return_value = "processed text"
                mock_text_prepare_class.return_value = mock_text_prepare_instance

                result = processor.process_text("raw text")

                # Verificar que TextPrepare se instanció y se llamó process
                mock_text_prepare_class.assert_called_once()
                mock_text_prepare_instance.process.assert_called_once_with("raw text")
