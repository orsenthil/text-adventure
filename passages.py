"""PassageLibrary: loads odyssey.mb.txt and serves curated Homer quotes."""

import re
import textwrap


class PassageLibrary:
    def __init__(self, filepath: str):
        self.books: dict[int, str] = {}
        self._load(filepath)
        self.curated = {
            # Act I
            "calypso_longing": {
                "book": 5,
                "contains": "round her cave there was a thick wood",
                "length": 400,
            },
            "calypso_raft": {
                "book": 5,
                "contains": "raft he is to reach fertile scheria",
                "length": 350,
            },
            "storm_at_sea": {
                "book": 5,
                "contains": "neptune, who was returning from the ethiopians",
                "length": 380,
            },
            # Act II
            "nausicaa_meeting": {
                "book": 6,
                "contains": "nausicaa, daughter to king alcinous",
                "length": 380,
            },
            "alcinous_feast": {
                "book": 7,
                "contains": "alcinous because he was king over the phaecians",
                "length": 380,
            },
            "lotus_warning": {
                "book": 9,
                "contains": "lotus-eater, who live on a food that comes from a kind of flower",
                "length": 300,
            },
            "polyphemus_blinding": {
                "book": 9,
                "contains": "no man is carrying off your sheep",
                "length": 420,
            },
            "bag_of_winds": {
                "book": 10,
                "contains": "ox-hide to hold the ways of the roaring winds",
                "length": 380,
            },
            "circe_enchantment": {
                "book": 10,
                "contains": "ompany to eurylochus, while i took command",
                "length": 400,
            },
            "tiresias_prophecy": {
                "book": 11,
                "contains": "teiresias should have a black sheep to himself",
                "length": 420,
            },
            "sirens_song": {
                "book": 12,
                "contains": "come here",
                "length": 380,
            },
            # Act III
            "ithaca_arrival": {
                "book": 13,
                "contains": "ulysses kept on turning his eyes towards the sun",
                "length": 350,
            },
            "swineherd_welcome": {
                "book": 14,
                "contains": "eumaeus",
                "length": 380,
            },
            "suitors_feast": {
                "book": 17,
                "contains": "suitors",
                "length": 380,
            },
            "bow_of_odysseus": {
                "book": 21,
                "contains": "took down the bow with its bow case from the peg",
                "length": 400,
            },
            "penelope_reunion": {
                "book": 23,
                "contains": "joy as she went up to her mistress",
                "length": 420,
            },
        }

    def _load(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()

        # Split on BOOK I, BOOK II, ... (Roman numerals)
        parts = re.split(r"\n(BOOK\s+[IVXLCDM]+)\n", raw)
        # parts[0] is the title/intro, then alternating: "BOOK X", text
        current_book = 0
        i = 0
        while i < len(parts):
            chunk = parts[i]
            if re.match(r"BOOK\s+[IVXLCDM]+", chunk.strip()):
                current_book = self._roman_to_int(chunk.strip().split()[-1])
                i += 1
                if i < len(parts):
                    self.books[current_book] = parts[i].lower()
            i += 1

    def _roman_to_int(self, s: str) -> int:
        vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
        result = 0
        prev = 0
        for ch in reversed(s.upper()):
            v = vals.get(ch, 0)
            if v < prev:
                result -= v
            else:
                result += v
            prev = v
        return result

    def get_passage(self, name: str) -> str:
        """Return a curated Homer excerpt, formatted for display."""
        if name not in self.curated:
            return ""
        spec = self.curated[name]
        text = self.books.get(spec["book"], "")
        # Normalise whitespace for matching (book text has newlines mid-sentence)
        normalised = " ".join(text.split())
        idx = normalised.find(spec["contains"])
        if idx == -1:
            return ""
        excerpt = normalised[idx: idx + spec["length"]]
        # Capitalise first letter, trim to last sentence boundary
        excerpt = excerpt.strip().capitalize()
        # Wrap and indent
        lines = textwrap.wrap(excerpt, width=68)
        return "\n".join("  " + ln for ln in lines)

    def format_passage(self, name: str) -> str:
        """Return passage surrounded by a decorative border."""
        text = self.get_passage(name)
        if not text:
            return ""
        border = "  " + "─" * 66
        return f"\n{border}\n{text}\n{border}\n"
