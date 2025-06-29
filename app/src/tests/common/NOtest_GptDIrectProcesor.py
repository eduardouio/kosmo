import pytest
from common import GPTDirectProcessor, TextPrepare
from common.AppLoger import loggin_event


@pytest.mark.django_db
class TestGptDirectProcesor():

    def setup_method(self):
        loggin_event('[TEST] Inicializando GPTDirectProcessor')
        self.gpt_direct_processor = GPTDirectProcessor()
        self.text_normalizer = TextPrepare()

    def test_openfile(self):
        with open("tests/testdata/dispoSantaClara.txt", "r") as file:
            dispo = file.read()

        text_normalized = self.text_normalizer.process(dispo)
        loggin_event('[TEST] Texto normalizado iniciando test de len')

        assert len(text_normalized.split("\n")) < len(dispo.split("\n"))
        assert len(text_normalized.split("\n")) == 63

        response = self.gpt_direct_processor.process_text(text_normalized)
        assert isinstance(response, list)
        assert len(response) == 63

    def test_large_dispo(self):
        with open("tests/testdata/dispoAnonymus2.txt", "r") as file:
            dispo = file.read()

        text_normalized = self.text_normalizer.process(dispo)
        loggin_event('[TEST] Texto normalizado iniciando test de len')

        assert len(text_normalized.split("\n")) == 149

        response = self.gpt_direct_processor.process_text(text_normalized)
        assert isinstance(response, list)
        assert len(response) == 149

    def test_specific_entries(self):
        """Test con entradas específicas para validar el procesamiento correcto"""
        loggin_event('[TEST] Iniciando test de entradas específicas')

        test_entries = [
            "1hb Country Blues 50/60 x 300 0,35/0,40",
            "1qb Playa Blanca 70 x 100 0,75",
            "1hb Priceless 50 x 400 0,30",
            "1 HB CANDY XPRESSION 50/60 (6/8)",
            "1 QB CANDY XPRESSION 70",
            "1 HB COUNTRY BLUES 50/60 (7/5)",
            "2hb Explorer 60 x 350 0,30",
            "1hb Explorer 70/80 x 300 0,35/0,40",
            "2hb Freedom 50 x 450 0,24",
            "1	EB	ANEMONE LEVANTE PINK 35CM	35CM	10	12	CXC +0.20",
            "3	EB	ANEMONE LEVANTE PINK 40CM	40CM	10	12	CXC +0.20",
            "3	EB	ANEMONE LEVANTE RED 25CM	25CM	10	12	CXC +0.20",
            "3	EB	ANEMONE LEVANTE RED 30CM	30CM	10	12	CXC +0.20"
        ]

        # Unir todas las entradas en un solo texto
        combined_text = "\n".join(test_entries)

        # Procesar el texto
        response = self.gpt_direct_processor.process_text(combined_text)

        # Validaciones generales
        assert isinstance(response, list)
        assert len(response) == len(test_entries)

        # Validar estructura de cada respuesta
        for i, item in enumerate(response):
            loggin_event(f'[TEST] Validando item {i}: {item}')

            # Cada item debe ser una lista con 7 elementos
            assert isinstance(item, list)
            assert len(item) == 7

            # Validar tipos básicos
            cantidad, modelo, variedades, medidas, tallos, precios = item[:6]

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
            f'[TEST] Test de entradas específicas completado exitosamente. Procesados {len(response)} items')

    def test_literal_output_validation(self):
        """Test que valida las salidas de forma literal contra valores esperados"""
        loggin_event('[TEST] Iniciando test de validación literal de salidas')

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
                "input": "1 HB CANDY XPRESSION 50/60 (6/8)",
                "expected": [1, "HB", ["CANDY XPRESSION", "CANDY XPRESSION"], [50, 60], [150, 200], [0, 0]]
            },
            {
                "input": "1 QB CANDY XPRESSION 70",
                "expected": [1, "QB", ["CANDY XPRESSION"], [70], [0], [0]]
            },
            {
                "input": "1 HB COUNTRY BLUES 50/60 (7/5)",
                "expected": [1, "HB", ["COUNTRY BLUES", "COUNTRY BLUES"], [50, 60], [175, 125], [0, 0]]
            },
            {
                "input": "2hb Explorer 60 x 350 0,30",
                "expected": [2, "HB", ["EXPLORER"], [60], [350], [0.30]]
            },
            {
                "input": "1hb Explorer 70/80 x 300 0,35/0,40",
                "expected": [1, "HB", ["EXPLORER", "EXPLORER"], [70, 80], [300, 0], [0.35, 0.40]]
            },
            {
                "input": "2hb Freedom 50 x 450 0,24",
                "expected": [2, "HB", ["FREEDOM"], [50], [450], [0.24]]
            },
            {
                "input": "1	EB	ANEMONE LEVANTE PINK 35CM	35CM	10	12	CXC +0.20",
                "expected": [1, "EB", ["ANEMONE LEVANTE", "PINK"], [35, 35], [10, 12], [0, 0]]
            },
            {
                "input": "3	EB	ANEMONE LEVANTE PINK 40CM	40CM	10	12	CXC +0.20",
                "expected": [3, "EB", ["ANEMONE LEVANTE", "PINK"], [40, 40], [10, 12], [0, 0]]
            },
            {
                "input": "3	EB	ANEMONE LEVANTE RED 25CM	25CM	10	12	CXC +0.20",
                "expected": [3, "EB", ["ANEMONE LEVANTE", "RED"], [25, 25], [10, 12], [0, 0]]
            },
            {
                "input": "3	EB	ANEMONE LEVANTE RED 30CM	30CM	10	12	CXC +0.20",
                "expected": [3, "EB", ["ANEMONE LEVANTE", "RED"], [30, 30], [10, 12], [0, 0]]
            }
        ]

        for i, test_case in enumerate(test_cases):
            loggin_event(f'[TEST] Procesando caso {i+1}: {test_case["input"]}')

            # Procesar entrada individual
            response = self.gpt_direct_processor.process_text(test_case["input"])

            # Validar que se devuelve exactamente un item
            assert len(response) == 1, f"Se esperaba 1 item, se obtuvo {len(response)}"

            actual = response[0]
            expected = test_case["expected"]

            # Validar estructura general
            assert len(actual) == 6, f"Se esperaban 6 elementos, se obtuvieron {len(actual)}"
            assert len(expected) == 6, f"Formato de test incorrecto: se esperaban 6 elementos en expected"

            # Validar cada campo individualmente
            assert actual[0] == expected[0], f"Cantidad: esperado {expected[0]}, obtenido {actual[0]}"
            assert actual[1].upper() == expected[1].upper(), f"Modelo: esperado {expected[1]}, obtenido {actual[1]}"

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
                assert abs(actual_price - expected_price) < 0.001, f"Precio {j}: esperado {expected_price}, obtenido {actual_price}"

            loggin_event(f'[TEST] Caso {i+1} validado exitosamente')

        loggin_event(f'[TEST] Validación literal completada exitosamente. {len(test_cases)} casos procesados')
