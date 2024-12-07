import pytest
from common import GPTProcessor


@pytest.mark.django_db
class TestGPTProcessor:

    def setup_method(self):
        self.gpt_processor = GPTProcessor()
        self.dispo_files = [
            {
                "file": "tests/testdata/dispAnonymus.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoAnonymus2.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoAnonymus3.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoAnonymus4.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoEcoFlor.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoEcoFlor2.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoEcoFlor3.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoEcoflor4.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma2.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma3.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoFlorAroma4.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoKosmo.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoKosmo2.txt",
                "lines_spected": 0,
                "spected_line_number": 11,
                'spected_line': [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoMatiz.txt",
                "lines_spected": 27,
                "spected_line_number": 11,
                "spected_line": [2, 'QB', 'KINGS CROSS', 25, [50], [0.60]]
            },
            {
                "file": "tests/testdata/dispoSantaClara.txt",
                "lines_spected": 74
            },
        ]

    def x_test_process_text_kosmo(self):
        file_text = open("tests/testdata/dispoKosmo.txt", "r")
        text_data = file_text.read().upper()
        file_text.close()
        text_data = [i.strip() for i in text_data.split("\n") if i != ""]
        text_data = '\n'.join(text_data)
        disponibility = self.gpt_processor.process_text(text_data)
        assert isinstance(disponibility, list)
        assert len(disponibility) == 40
        # 1qb Hermosa 50/70 x 100 0,50/0,70
        spected_line_17 = [
            1, 'QB', 'HERMOSA', 100, [50, 70], [0.50, 0.70]
        ]
        assert disponibility[17] == spected_line_17

    def x_test_process_text_kosmo_2(self):
        file_text = open("tests/testdata/dispoKosmo2.txt", "r")
        text_data = file_text.read().upper()
        file_text.close()
        text_data = [i.strip() for i in text_data.split("\n") if i != ""]
        text_data = '\n'.join(text_data)
        disponibility = self.gpt_processor.process_text(text_data)
        assert isinstance(disponibility, list)
        assert len(disponibility) == 78
        # 1qb Secret Garden 40/50/60 x 100 0,30/0,34/0,38
        spected_line_70 = [
            1, 'QB', 'SECRET GARDEN', 100, [40, 50, 60], [0.30, 0.34, 0.38]
        ]
        assert disponibility[70] == spected_line_70

    def test_process_text_anonymus(self):
        file_text = open("tests/testdata/dispAnonymus.txt", "r")
        text_data = file_text.read().upper()
        file_text.close()
        text_data = [i.strip() for i in text_data.split("\n") if i != ""]
        text_data = '\n'.join(text_data)
        disponibility = self.gpt_processor.process_text(text_data)
        assert isinstance(disponibility, list)
        assert len(disponibility) == 40
        # 1qb Hermosa 50/70 x 100 0,50/0,70
        spected_line_17 = [
            1, 'QB', 'HERMOSA', 100, [50, 70], [0.50, 0.70]
        ]
        assert disponibility[17] == spected_line_17

    def test_process_text(self):
        pass
    
    def text_prepare(self, file_name):
        text_search = [
            'TIPO B',
            'KOSMO',
            'AVAILABILITY',
            'HOLA',
            'BUENOS DIAS',
            'DÍAS',
            'KOSMO',
            'ECOFLOR',
            'FLORAROMA'
        ]
        file_text = open(file_name, "r")
        text_data = file_text.read().upper()
        file_text.close()
        text_data = [i.strip() for i in text_data.split("\n") if i != ""]
        text_data = [i for i in text_data if i not in text_search]
        text_data = '\n'.join(text_data)
        return text_data
