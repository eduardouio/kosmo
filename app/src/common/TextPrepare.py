import re


class TextPrepare:
    def __init__(self):

        self.text_to_delete = {
            'TIPO B',
            'KOSMO',
            'HOLA',
            'AMIGO',
            'BUENOS DIAS',
            'AVAILABILITY',
            'DÍAS',
            'ECOFLOR',
            'FLORAROMA',
            'DISPO',
            'DISPONIBILIDAD',
            'DIPONIBILIDAD',
            '*',
        }

        self.characters_to_replace = {
            'Á': 'A',
            'É': 'E',
            'Í': 'I',
            'Ó': 'O',
            'Ú': 'U',
        }

        self.date_regex = re.compile(r'\d{2}[/.-]\d{2}[/.-]\d{4}')

    def normalize_text(self, text):
        text = text.upper().strip()
        return ''.join(
            self.characters_to_replace.get(char, char) for char in text
        )

    def should_skip_line(self, line):
        return (
            self.date_regex.search(line) or
            any(word in line for word in self.text_to_delete)
        )

    def process(self, text):
        if not text:
            return None

        text = self.normalize_text(text)

        processed_text = [
            line.replace('+ EXTRA', '').strip()
            for line in text.split("\n")
            if line.strip() and not self.should_skip_line(line.strip())
        ]

        return '\n'.join(processed_text) if processed_text else None
