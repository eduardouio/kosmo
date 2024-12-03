import pytest
from common import GPTProcessor
import time


@pytest.mark.django_db
class TestGPTProcessor:

    def setup_method(self):
        self.gpt_processor = GPTProcessor()

    def test_proccess_text(self):
        file_text = open("tests/testdata/dispoKosmo.txt", "r")
        text_data = file_text.read()
        file_text.close()
        start = time.time()
        disponibility = self.gpt_processor.process_text(text_data)
        end = time.time()
        # TIEMPO EN SEGUNDOS