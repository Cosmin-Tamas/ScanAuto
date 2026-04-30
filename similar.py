
"""

Exemplu de utilizare
-----
>>> sim = build_romanian_decoder()
>>> result = sim.predict_plate("AR01ABC")

result este de tip: list[PlateResult]

iar daca ai nevoie de nmarul corectat faci: result[i].corrected

"""


from __future__ import annotations
from dataclasses import dataclass, field
from rapidfuzz.distance import Levenshtein
from test_cases import DATA
#from OCR_conversion import DIGIT_MAP, LETTER_MAP, MULTI_CHAR

brk = False

# ── normalisation ─────────────────────────────────────────────────────────────

def normalize_input(s: str) -> str:
    return s.upper().replace(" ", "")


# ── char-type helpers ─────────────────────────────────────────────────────────

def _char_type(ch: str) -> str:
    if ch.isalpha():  return "L"
    if ch.isdigit(): return "D"
    return "?"

def _to_pattern(s: str) -> str:
    return "".join(_char_type(c) for c in s)


# ── result type ───────────────────────────────────────────────────────────────

@dataclass
class PlateResult:
    corrected: str = ""
    initial:   str = ""
    label:     str = "INVALID"
    pattern:   str = "INVALID"
    score:     float = 0.0

    @property
    def is_valid(self) -> bool:
        return self.label != "INVALID"
    
    def __str__(self) -> str:
        return (
            f"{self.initial:<10} | "
            f"{self.corrected:<10} | "
            f"{self.label:<20} | "
            f"{self.pattern:<10} | "
            f"{self.score:>5.2f}"
        )
    
    def __repr__(self) -> str:
        return self.__str__()


# ── scorer ────────────────────────────────────────────────────────────────────

def _score(plate: str, pattern: str) -> float:
    """
    Levenshtein normalizat pe șiruri de tipuri de caractere.

    Bonus de lungime: vrem ca un candidat de 7 caractere care 
    se potrivește perfect cu un pattern de 7 caractere să fie 
    preferat în fața unui candidat de 8 caractere care necesită o singură modificare.

    Pentru asta, aplicăm un bonus mic proporțional cu cât din pattern 
    este acoperit (lungimea_candidatului / lungimea_patternului), 
    limitat la maxim 1.0, astfel încât candidații mai lungi decât pattern-ul 
    să nu aibă un avantaj artificial.
    """
    p = _to_pattern(plate)
    max_len = max(len(p), len(pattern))
    if max_len == 0:
        return 0.0

    dist = Levenshtein.distance(p, pattern)
    similarity = 1.0 - dist / max_len

    # Prefer candidates whose length matches the pattern exactly.
    # A perfect-match shorter candidate scores 1.0; a longer one is capped.
    coverage = min(len(plate), len(pattern)) / len(pattern) if pattern else 0.0
    return similarity * coverage


# ── corrector ─────────────────────────────────────────────────────────────────

def _apply_map(ch: str, expected: str) -> str:
    """Mapeaza litera la cifra si invers infunctie de 'expected' """
    if expected == "L":
        return LETTER_MAP.get(ch, ch)
    if expected == "D":
        return DIGIT_MAP.get(ch, ch)
    return ch


def _correct(plate: str, pattern: str) -> str:
    """
    Corecteaza numarul in functie de pattern. 
    Corectiile se aplica doar daca tipul caracterului este diferit de tipul asteptat
    din pattern. 
    Face split sau merge daca gaseste greseli

    Un “split” de la 1 caracter la 2 (de ex. „W” → „VV”) este încercat doar atunci când:

    1. Tipul caracterului din placă nu corespunde tipului așteptat de poziția curentă din pattern și
    2. Pattern-ul are loc pentru două poziții (adică j+1 < len(pattern)) și
    3. Ambele caractere rezultate se potrivesc tipurilor așteptate.

    Fără condiția (1), un „W” corect aflat într-o poziție de tip literă ar fi totuși împărțit în mod greșit.
    """
    plate   = plate.upper()
    pattern = pattern.upper()

    i = j = 0
    out: list[str] = []

    while i < len(plate) and j < len(pattern):
        expected = pattern[j]   # 'L' or 'D'
        ch       = plate[i]
        mismatch = _char_type(ch) != expected

        # --- MERGE ---
        if mismatch and i + 1 < len(plate):
            pair   = ch + plate[i + 1]
            mapped = MULTI_CHAR.get(pair)
            if mapped and len(mapped) == 1:
                out.append(_apply_map(mapped, expected))
                i += 2
                j += 1
                continue

        # --- SPLIT ---
        if mismatch and j + 1 < len(pattern):
            mapped = MULTI_CHAR.get(ch)
            if mapped and len(mapped) == 2:
                out.append(_apply_map(mapped[0], pattern[j]))
                out.append(_apply_map(mapped[1], pattern[j + 1]))
                i += 1
                j += 2
                continue

        if mismatch:
            out.append(_apply_map(ch, expected))
        else:
            out.append(ch)
        i += 1
        j += 1

    while i < len(plate):
        out.append(plate[i])
        i += 1

    return "".join(out)


# --- GENERATOR DE CANDIDATI ---
def _generate_candidates(plate: str, min_len: int, max_len: int) -> list[str]:
    """
    All unique substrings of plate with length in [min_len, max_len],
    plus "one char removed" variants to handle spurious inserted characters.

    Generation order:
      1. Normal substrings, longest first.
      2. Every valid substring with one character removed at any position
         (including first and last), so e.g. "IAR01ABC" → "AR01ABC".
    Final list is sorted longest-first before return.
    """
    seen: set[str] = set()
    out:  list[str] = []

    def _add(s: str) -> None:
        if min_len <= len(s) <= max_len and s not in seen:
            seen.add(s)
            out.append(s)

    # 1. Normal substrings
    for length in range(min(max_len, len(plate)), min_len - 1, -1):
        for i in range(len(plate) - length + 1):
            _add(plate[i : i + length])

    # 2. One-char-removed variants
    #    Apply to the plate itself AND to any substring that is longer than
    #    min_len (so chopping it still yields a candidate of valid length).
    #    We iterate over a snapshot of `out` plus the plate, deduplicated.
    sources = [plate] + [s for s in list(out) if len(s) > min_len]
    for source in sources:
        for i in range(len(source)):          # ALL positions: 0..len-1
            chopped = source[:i] + source[i + 1:]
            _add(chopped)

    # Longest first so the scoring loop meets best candidates early.
    out.sort(key=len, reverse=True)
    return out

# ── main class ────────────────────────────────────────────────────────────────

@dataclass
class Similar:
    """
    Decoder OCR

    Exemplu de utilizare
    -----
    >>> sim = Similar()
    >>> sim.add_pattern("LLDDLLL", "county_standard")
    >>> result = sim.predict_plate("AR01ABC")
    >>> print(result.corrected, result.label)
    AR01ABC county_standard
    """
    _patterns: list[dict] = field(default_factory=list, repr=False)
    _predictions: list[PlateResult] = field(default_factory=list)

    def add_pattern(self, pattern: str, label: str) -> None:
        self._patterns.append({"pattern": pattern.upper(), "label": label})

    def predict_plate(
        self,
        plate:     str,
        threshold: float = 0.75,
        min_len:   int   = 6,
        max_len:   int   = 8,
    ) -> list[PlateResult]:
        """
    Pipeline complet: normalizare → generare candidați → scorare → corectare → rescorare.
    Early-exit-ul este intenționat conservator: 
    ignorăm o pereche (candidat, pattern) doar atunci când scorul brut 
    este mai mic decât jumătate din prag, ceea ce înseamnă că nici după 
    corectare nu ar fi realist să depășească pragul de acceptare. 
    Astfel se păstrează viteza pe Raspberry Pi, fără a elimina candidații care pot fi corectați.
        """
        plate = normalize_input(plate)
        best  = PlateResult()
        self._predictions = []

        half_threshold = threshold * 0.5

        for candidate in _generate_candidates(plate, min_len, max_len):
            for p in self._patterns:
                # scoring initial
                score = _score(candidate, p["pattern"])

                # ignora daca e prea mic scorul
                if score < half_threshold:
                    continue

                # corecteaza pattern-ul si recalculeaza scorul
                corrected   = _correct(candidate, p["pattern"])
                score = _score(corrected,  p["pattern"])

                label = p["label"]

                # append doar daca scorul este 1 si numarul prezis exista in lista de judete
                if score == 1 and any(corrected.startswith(pref) for pref in start_with.get(label, [])):
                    self._predictions.append(
                        PlateResult(
                            initial=candidate,
                            corrected=corrected,
                            label=label,
                            pattern=p["pattern"],
                            score=score,
                        )
                    )

        return self._predictions

# ── convenience: build all Romanian patterns ──────────────────────────────────

def build_romanian_decoder(threshold: float = 0.75) -> Similar:
    """
    Returnează o instanță Similar preîncărcată cu 
    toate pattern-urile pentru plăcuțele de înmatriculare din România. 
    Se poate apela direct predict_plate() pe această instanță.
    """
    sim = Similar()
    for patterns in pattern_groups.values():
        for pat, label in patterns:
            sim.add_pattern(pat, label)
    return sim

def testeaza():
    sim = build_romanian_decoder()

    for plate, expected_pattern in DATA:
        predicted_plate = sim.predict_plate(plate)

        print(plate)
        for p_p in predicted_plate:
            print(p_p)
        print("-----------------------------------------------")
        if brk:
            break

    #print(f"\nAccuracy: {correct_count}/{len(DATA)} = {correct_count / len(DATA):.2%}")>>

DIGIT_MAP = {
    # letter → digit confusion
    "O": "0",
    "Q": "0",
    "D": "0",   # sometimes hollow D-like shapes
    "I": "1",
    "l": "1",
    "Z": "2",
    "S": "5",
    "B": "8",
    "G": "6",
    "L": "1",

    # symbol → digit confusion (VERY common in OpenCV)
    "@": "0",
    "#": "0",
    "$": "5",
    "%": "0",
    "&": "8",
    "*": "",
    "!": "1",
    "|": "1",
    "(": "0",
    ")": "0",
    "{": "0",
    "}": "0",
    "[": "1",
    "]": "1",
    "/": "1",
    "\\": "1",
    ".": "",
    ",": "",
    ":": "",
    ";": "",
    "'": "",
    "\"": "",

    # OCR blur / merge artifacts
    "rn": "11",
    "cl": "1",
    "vv": "11",
}

LETTER_MAP = {
    # digit → letter confusion (most important)
    "0": "O",
    "1": "I",
    "2": "Z",
    "3": "E",   # sometimes seen in stylized fonts
    "4": "A",
    "5": "S",
    "6": "G",
    "7": "T",
    "8": "B",
    "9": "G",

    # symbol → letter confusion
    "@": "A",
    "#": "H",
    "$": "S",
    "%": "X",
    "&": "B",
    "*": "",
    "!": "I",
    "|": "I",
    "/": "I",
    "\\": "I",
    "(": "C",
    ")": "C",
    "{": "C",
    "}": "C",
    "[": "L",
    "]": "L",
    "<": "V",
    ">": "V",
    "?": "Q",
    ".": "",
    ",": "",
    ":": "",
    ";": "",
    "\"": "",
    "'": "",

    # OCR multi-char artifacts (blur / merge / split)
    "rn": "M",
    "nn": "M",
    "cl": "D",
    "vv": "W",
    "uu": "U",
    "li": "H",
    "il": "H",

    # shape-based OCR confusion
    "—": "I",
    "_": "I",
}

MULTI_CHAR = {
    # =========================
    # 2 → 1 (merge errors)
    # =========================
    "VV": "W",
    "WW": "W",
    "II": "H",
    "NN": "M",
    "CL": "D",
    "RN": "M",
    "RM": "M",
    "OO": "0",
    "00": "0",
    "II": "1",
    "LL": "U",

    # =========================
    # 1 → 2 (split errors)
    # =========================
    "W": "VV",
    "M": "NN",
    "H": "II",
    "D": "CL",
    "U": "LL",
    "0": "OO",
    "1": "II"
}

start_with = {
    "county_standard": [
        "AB","AR","AG","BC","BH","BN","BR","BT","BV","BZ",
        "CL","CS","CJ","CT","CV","DB","DJ","GL","GR","GJ",
        "HR","HD","IL","IS","IF","MM","MH","MS","NT","OT",
        "PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL","VN"
    ],

    "bucharest_standard": ["B"],
    "bucharest_short": ["B"],

    "mai_plate": ["MAI"],
    "diplomatic_plate": ["CD", "TC"],

    "temporary_plate": [
        "AB","AR","AG","BC","BH","BN","BR","BT","BV","BZ",
        "CL","CS","CJ","CT","CV","DB","DJ","GL","GR","GJ",
        "HR","HD","IL","IS","IF","MM","MH","MS","NT","OT",
        "PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL","VN"
    ],

    "military_plate": ["A"]
}

pattern_groups = {
    "standard": [
        ("LLDDLLL",  "county_standard"),
        #("LLDDDLLL", "county_3digit"),
    ],
    "bucharest": [
        ("LDDDLLL", "bucharest_standard"),
        ("LDDLLL",  "bucharest_short"),
    ],
    "special": [
        ("LLLDDDDD", "mai_plate"),
        ("LLDDDDDD", "temporary_plate"),
        ("LDDDDD",   "military_plate"),
        ("LLDDDLLL", "diplomatic_plate"),
    ],
}

if __name__ == "__main__":
    testeaza()