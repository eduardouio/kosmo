import pytest
from common import TextPrepare


class Test_TestPrepare():

    def setup_method(self):
        self.text_prepare = TextPrepare()

    def test_text_prepare_no_valid(self):
        text = "Hola, buenos        días"
        text = self.text_prepare.process(text)
        assert text is None
        assert self.text_prepare.process("") is None
        assert self.text_prepare.process(None) is None

    def test_text_prepare_kosmo(self):
        file = "tests/testdata/dispoKosmo2.txt"
        with open(file, "r") as f:
            text = f.read()

        text = self.text_prepare.process(text)
        assert len(text.split("\n")) == 68

    def test_text_prepare_floraroma(self):
        file = "tests/testdata/dispoFlorAroma4.txt"
        with open(file, "r") as f:
            text = f.read()

        text = self.text_prepare.process(text)
        assert len(text.split("\n")) == 75

    def test_text_prepare_ecoflor(self):
        file = "tests/testdata/dispoEcoflor4.txt"
        with open(file, "r") as f:
            text = f.read()

        text = self.text_prepare.process(text)
        assert len(text.split("\n")) == 99

    def test_text_prepare_ecoflor2(self):
        file = "tests/testdata/dispoEcoFlor2.txt"
        with open(file, "r") as f:
            text = f.read()

        text = self.text_prepare.process(text)
        assert len(text.split("\n")) == 63

    def test_text_prepare_matiz(self):
        file = "tests/testdata/dispoMatiz.txt"
        with open(file, "r") as f:
            text = f.read()

        text = self.text_prepare.process(text)
        assert len(text.split("\n")) == 27

    def test_text_prepare_santa_clara(self):
        file = "tests/testdata/dispoSantaClara.txt"
        with open(file, "r") as f:
            text = f.read()

        text = self.text_prepare.process(text)
        assert len(text.split("\n")) == 63

    def test_text_valid(self):
        text = """
            Hola
            ********
            Floraroma es un ejemplo
            Kosmo
            12/12/2023
            Buenos días
            Texto válido
        """
        text = self.text_prepare.process(text)
        assert text == "TEXTO VALIDO"

    def test_with_extra(self):
        text = "LUCIANO 50 cm + extra"
        text = self.text_prepare.process(text)
        assert text == "LUCIANO 50 CM"
