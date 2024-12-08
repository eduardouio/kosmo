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
                "spected_line": [1, 'QB', 'COTTON XPRESSION', 0, 0, [40], [0]]
            },
            {
                "file": "tests/testdata/dispoAnonymus3.txt",
                "lines_spected": 49,
                "spected_line_number": 33,
                "spected_line": [1, 'QB', 'ORANGE BOWL', 0, 0, [40], [0]]
            },
            {
                "file": "tests/testdata/dispoAnonymus4.txt",
                "lines_spected": 49,
                "spected_line_number": 10,
                "spected_line": [2, 'HB', 'COTTON XPRESSION', 0, [50, 60], [0.50, 0.60]]
            },
            {
                "file": "tests/testdata/dispoEcoFlor.txt",
                "lines_spected": 94,
                "spected_line_number": 94,
                "spected_line": [1, 'QB', 'VENDELA', 0, 0, [60, 70], [0, 0]]
            },
            {
                "file": "tests/testdata/dispoEcoFlor2.txt",
                "lines_spected": 63,
                "spected_line_number": 18,
                "spected_line": [1, 'QB', 'FREEDOM', 0, 0, [90], [0]]
            },
            {
                "file": "tests/testdata/dispoEcoFlor3.txt",
                "lines_spected": 49,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'COOL WATER', 25, 0.60, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoEcoflor4.txt",
                "lines_spected": 99,
                "spected_line_number": 4,
                "spected_line": [1, 'QB', 'BE SWEET', 0, 0, [90], [0]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma.txt",
                "lines_spected": 32,
                "spected_line_number": 17,
                "spected_line": [1, 'QB', 'PHOENIX', 0, 0, [40, 50], [0.40, 0.50]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma2.txt",
                "lines_spected": 37,
                "spected_line_number": 20,
                "spected_line": [1, 'HB', 'PLAYA BLANCA', 0, 0.50, [40], [0.50]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma3.txt",
                "lines_spected": 61,
                "spected_line_number": 35,
                "spected_line": [3, 'HB', 'NEWSFLASH', 0, 0, [40], [0]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma4.txt",
                "lines_spected": 75,
                "spected_line_number": 54,
                "spected_line": [1, 'HB', 'VERSILIA', 0, 0.21, [50], [0.24]]
            },
            {
                "file": "tests/testdata/dispoKosmo.txt",
                "lines_spected": 40,
                "spected_line_number": 1,
                "spected_line": [1, 'HB', 'EXPLORER', 250, 0, [40, 50], [0.40, 0.50]]
            },
            {
                "file": "tests/testdata/dispoKosmo2.txt",
                "lines_spected": 68,
                "spected_line_number": 8,
                'spected_line': [4, 'QB', 'PLAYA BLANCA', 100, 0.90, [50], [0.90]]
            },
            {
                "file": "tests/testdata/dispoMatiz.txt",
                "lines_spected": 27,
                "spected_line_number": 20,
                "spected_line": [3, 'QB', 'ORANGE CRUSH', 25, 0.28, [40], [0.28]]
            },
            {
                "file": "tests/testdata/dispoSantaClara.txt",
                "lines_spected": 63,
                "spected_line_number": 23,
                "spected_line": [2, 'HB', 'FREEDOM', 0, 0, [60], [0]],
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
            0/0
            assert len(result) == test['lines_spected']
            if test['lines_spected'] > 0:
                assert result[test['spected_line_number'] -1]  == test['spected_line']
