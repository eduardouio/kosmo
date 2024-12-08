import pytest
import random
from common import GPTProcessor, TextPrepare


@pytest.mark.django_db
class TestGPTProcessor:

    def setup_method(self):
        self.gpt_processor = GPTProcessor()
        self.text_normalizer = TextPrepare()
        self.dispo_files = [
            {
                "file": "tests/testdata/dispAnonymus.txt",
                "lines_spected": 27,
                "spected_line_number": 20,
                "spected_line": [1, 'HB', 0, 0, 'SHIMMER', [50, 60, 70], [0, 0, 0]]
            },
            {
                "file": "tests/testdata/dispoAnonymus2.txt",
                "lines_spected": 87,
                "spected_line_number": 12,
                "spected_line": [1, 'QB', 0, 0, 'COTTON XPRESSION', [40], [0]]
            },
            {
                "file": "tests/testdata/dispoAnonymus3.txt",
                "lines_spected": 49,
                "spected_line_number": 33,
                "spected_line": [1, 'QB', 0, 0, 'ORANGE BOWL', [40], [0]]
            },
            {
                "file": "tests/testdata/dispoAnonymus4.txt",
                "lines_spected": 49,
                "spected_line_number": 10,
                "spected_line": [1, 'HB', 0, 40, 'COTTON XPRESSION', [50, 60], [0.50, 0.60]]
            },
            {
                "file": "tests/testdata/dispoEcoFlor.txt",
                "lines_spected": 94,
                "spected_line_number": 94,
                "spected_line": [1, 'QB', 0, 0, 'VENDELA', [60, 70], [0, 0]]
            },
            {
                "file": "tests/testdata/dispoEcoFlor2.txt",
                "lines_spected": 63,
                "spected_line_number": 18,
                "spected_line": [1, 'QB', 0, 0, 'FREEDOM', [90], [0]]
            },
            {
                "file": "tests/testdata/dispoEcoFlor3.txt",
                "lines_spected": 49,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 25, 0.60, 'COOL WATER', [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoEcoflor4.txt",
                "lines_spected": 99,
                "spected_line_number": 4,
                "spected_line": [1, 'QB', 0, 0, 'BE SWEET', [90], [0]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma.txt",
                "lines_spected": 32,
                "spected_line_number": 17,
                "spected_line": [1, 'QB', 0, 0, 'PHOENIX', [40, 50], [0.40, 0.50]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma2.txt",
                "lines_spected": 37,
                "spected_line_number": 20,
                "spected_line": [1, 'HB', 0, 0.50, 'PLAYA BLANCA', [40], [0.50]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma3.txt",
                "lines_spected": 61,
                "spected_line_number": 35,
                "spected_line": [3, 'HB', 0, 0, 'NEWSFLASH', [40], [0]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma4.txt",
                "lines_spected": 75,
                "spected_line_number": 54,
                "spected_line": [1, 'HB', 0, 0.24,  'VERSILIA', [50], [0.24]]
            },
            {
                "file": "tests/testdata/dispoKosmo.txt",
                "lines_spected": 40,
                "spected_line_number": 1,
                "spected_line": [1, 'HB', 250, 0, 'EXPLORER', [40, 50], [0.40, 0.50]]
            },
            {
                "file": "tests/testdata/dispoKosmo2.txt",
                "lines_spected": 68,
                "spected_line_number": 8,
                'spected_line': [4, 'QB', 100, 0.90, 'PLAYA BLANCA', [50], [0.90]]
            },
            {
                "file": "tests/testdata/dispoMatiz.txt",
                "lines_spected": 27,
                "spected_line_number": 20,
                "spected_line": [3, 'QB', 25, 0.28, 'ORANGE CRUSH', [40], [0.28]]
            },
            {
                "file": "tests/testdata/dispoSantaClara.txt",
                "lines_spected": 63,
                "spected_line_number": 23,
                "spected_line": [2, 'HB', 0, 0, 'FREEDOM', [60], [0]],
            },
        ]

    def test_process(self):
        total_test = [random.choice(self.dispo_files) for _ in range(2)]
        for test in total_test:
            file_text = open(test['file'], "r")
            text_data = file_text.read()
            file_text.close()
            text_data = self.text_normalizer.process(text_data)
            result = self.gpt_processor.process_text(text_data)
            assert len(result) == test['lines_spected']
            if test['lines_spected'] > 0:
                assert result[test['spected_line_number'] -1] == test['spected_line']
