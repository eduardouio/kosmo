import re
import difflib
from products.models import Product


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
            'PROMO',
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
            ',': '.',
        }

        self.date_regex = re.compile(r'\d{2}[/.-]\d{2}[/.-]\d{4}')
        # Cache de variedades (se carga on-demand)
        self._varieties_cache = None
        # Reemplazos manuales rápidos antes de fuzzy
        self.manual_replacements = {
            'FREDOM': 'FREEDOM',
            'FREDDOM': 'FREEDOM',
            'FREEDOM': 'FREEDOM',  # idempotente
            'CANDLE LIGHT': 'CANDLELIGHT',
            'CANDLELIGTH': 'CANDLELIGHT',
            'COTTON X-PRESSION': 'COTTON XPRESSION',
            'COTTON X PRESSION': 'COTTON XPRESSION',
            'COTTON X-PRESION': 'COTTON XPRESSION',
            'COTTON XPRETION': 'COTTON XPRESSION',
        }
        # Modelos válidos para detectar segmento de variedad
        self.valid_models = {'HB', 'QB', 'EB', 'FB'}
        self.measure_pattern = re.compile(r'^\d+(?:[/,-]\d+)*(?:CM)?$')

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

        processed_text = []
        for raw_line in text.split("\n"):
            line = raw_line.strip()
            if not line or self.should_skip_line(line):
                continue
            line = line.replace('+ EXTRA', '').strip()
            corrected = self._correct_varieties_in_line(line)
            processed_text.append(corrected)

        return '\n'.join(processed_text) if processed_text else None

    # ---------------- Variedades ----------------
    def _load_varieties(self):
        if self._varieties_cache is None:
            try:
                # Asumimos campo 'name' como variedad
                names = list(
                    Product.objects.values_list('name', flat=True)
                )
            except Exception:
                names = []
            # Normalizar a MAYÚSCULAS sin espacios extremos
            self._varieties_cache = sorted({
                n.strip().upper() for n in names
                if n and n.strip()
            })
        return self._varieties_cache

    def _normalize_key(self, s: str) -> str:
        return re.sub(r'[^A-Z0-9]', '', s.upper())

    def _best_match(self, phrase: str):
        varieties = self._load_varieties()
        if not varieties:
            return None
        # Intento directo
        if phrase in varieties:
            return phrase
        # Fuzzy por SequenceMatcher
        candidates = difflib.get_close_matches(
            phrase, varieties, n=1, cutoff=0.82
        )
        return candidates[0] if candidates else None

    def _correct_varieties_in_line(self, line: str) -> str:
        """Detecta y corrige la sección de variedades dentro de la línea.

        Estrategia:
    1. Token con cantidad+modelo (4HB) o cantidad y modelo separados.
    2. Tokens hasta medida (número / lista) o 'X'.
    3. Frase variedad -> reemplazos manuales + fuzzy.
        4. Reinyectar variedad corregida manteniendo el resto intacto.
        """
        try:
            tokens = line.split()
            if len(tokens) < 2:
                return line
            # Solo detectar variedad (quantity/model no se usan aquí)
            first = tokens[0]
            # Caso combinado: 3HB
            m = re.match(r'^(\d+)([A-Z]{2})$', first)
            if m and m.group(2) in self.valid_models:
                variety_start = 1
            else:
                # Caso separado: 3 HB
                if (first.isdigit() and len(tokens) > 1 and
                        tokens[1] in self.valid_models):
                    variety_start = 2
                else:
                    return line  # patrón no reconocido
            # Encontrar fin de variedad
            variety_end = variety_start
            for i in range(variety_start, len(tokens)):
                t = tokens[i]
                if (self.measure_pattern.match(t) or t == 'X' or
                        t.replace('/', '').isdigit()):
                    break
                variety_end = i + 1
            variety_tokens = tokens[variety_start:variety_end]
            if not variety_tokens:
                return line
            original_phrase = ' '.join(variety_tokens)
            phrase = original_phrase
            # Reemplazos manuales multicomponentes primero
            manual_hit = self.manual_replacements.get(phrase)
            if not manual_hit:
                # También probar sin espacios (ej CANDLE LIGHT)
                manual_hit = self.manual_replacements.get(
                    phrase.replace(' ', '')
                )
            if manual_hit:
                corrected = manual_hit
            else:
                # Fuzzy sobre frase completa
                corrected = self._best_match(phrase)
                if not corrected and ' ' in phrase:
                    # Intentar cada palabra por separado y reconstruir
                    corrected_parts = []
                    for part in phrase.split():
                        manual_part = self.manual_replacements.get(part)
                        if manual_part:
                            corrected_parts.append(manual_part)
                            continue
                        bm = self._best_match(part)
                        corrected_parts.append(bm if bm else part)
                    corrected = ' '.join(corrected_parts)
            if corrected and corrected != original_phrase:
                # Sustituir en tokens
                new_tokens = (
                    tokens[:variety_start] +
                    corrected.split() +
                    tokens[variety_end:]
                )
                return ' '.join(new_tokens)
            return line
        except Exception:
            return line
