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
