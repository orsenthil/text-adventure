"""CommandParser: tokenizes player input and dispatches to (verb, noun) pairs."""

import re


# Verbs that consume two words ("talk to", "ask about")
TWO_WORD_VERBS = {
    "talk to": "talk",
    "speak to": "talk",
    "ask about": "ask",
    "look at": "examine",
    "pick up": "take",
    "tell story": "tell_story",
}

# Single-word verb aliases
VERB_ALIASES = {
    "examine": "examine",
    "x": "examine",
    "inspect": "examine",
    "look": "look",
    "l": "look",
    "take": "take",
    "get": "take",
    "grab": "take",
    "drop": "drop",
    "leave": "drop",
    "inventory": "inventory",
    "inv": "inventory",
    "i": "inventory",
    "use": "use",
    "wear": "wear",
    "put on": "wear",
    "shoot": "shoot",
    "fire": "shoot",
    "go": "go",
    "travel": "go",
    "sail": "go",
    "walk": "go",
    "talk": "talk",
    "speak": "talk",
    "ask": "ask",
    "help": "help",
    "h": "help",
    "save": "save",
    "load": "load",
    "quit": "quit",
    "q": "quit",
    "exit": "quit",
    "remember": "remember",
    "tell": "tell_story",
}


def _strip_articles(s: str) -> str:
    """Remove leading 'the', 'a', 'an' from a noun phrase."""
    return re.sub(r"^(the|a|an)\s+", "", s).strip()


class CommandParser:
    def parse(self, raw: str) -> tuple[str, str | None]:
        """
        Return (verb, noun_or_None).
        verb is a canonical string like 'examine', 'take', 'go', etc.
        noun is None when the verb takes no object.
        """
        text = raw.lower().strip()
        if not text:
            return ("empty", None)

        # Check two-word verbs first (order matters — longest match)
        for phrase, canonical in TWO_WORD_VERBS.items():
            if text.startswith(phrase):
                noun = text[len(phrase):].strip()
                noun = _strip_articles(noun) or None
                return (canonical, noun)

        # Single-word verb
        tokens = text.split()
        verb_word = tokens[0]
        canonical = VERB_ALIASES.get(verb_word)

        if canonical is None:
            return ("unknown", text)

        noun = _strip_articles(" ".join(tokens[1:])) or None
        return (canonical, noun)
