import re


class TextPrepare(object):

    def __init__(self):
        self.text_to_delete = [
            'TIPO B',
            'KOSMO',
            'HOLA',
            'AMIGO',
            'BUENOS DIAS',
            'AVAILABILITY',
            'HOLA',
            'DÍAS',
            'KOSMO',
            'ECOFLOR',
            'FLORAROMA',
            'DISPO',
            'DISPONIBILIDAD',
            'DIPONIBILIDAD',
        ]
        self.characters_to_replace = [
            {'source': 'Á', 'new': 'A'},
            {'source': 'É', 'new': 'E'},
            {'source': 'Í', 'new': 'I'},
            {'source': 'Ó', 'new': 'O'},
            {'source': 'Ú', 'new': 'U'},
        ]

        self.date_regex = re.compile(r'\d{2}/\d{2}/\d{4}')
        self.date_regex2 = re.compile(r'\d{2}-\d{2}-\d{4}')
        self.date_regex3 = re.compile(r'\d{2}\.\d{2}\.\d{4}')

    def process(self, text):
        if text == "" or text is None:
            return None

        text = text.upper().strip()

        for char in self.characters_to_replace:
            text = text.replace(char['source'], char['new'])

        proccessed_text = []
        for itm in text.split("\n"):
            itm = itm.strip()
            if self.date_regex.search(itm) or self.date_regex2.search(itm) or self.date_regex3.search(itm):
                continue

            if any(j in itm for j in self.text_to_delete):
                continue

            proccessed_text.append(itm)

        text = [i.strip() for i in proccessed_text if i != ""]
        if len(text) == 0:
            return None

        text = '\n'.join(text)
        return text
