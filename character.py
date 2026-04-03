"""Character: an NPC with keyword-driven dialogue."""

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player


class Character:
    def __init__(
        self,
        name: str,
        aliases: list[str],
        greeting: str,
        dialogue_tree: dict[str, str] | None = None,
        # topic -> suppress_if(player): hide this topic from menu when True
        topic_suppress: dict[str, Callable[["Player"], bool]] | None = None,
    ):
        self.name = name
        self.aliases = aliases
        self.greeting = greeting
        self.dialogue_tree: dict[str, str] = dialogue_tree or {}
        self.topic_suppress: dict[str, Callable] = topic_suppress or {}
        self.has_given_item: bool = False
        self.greeted: bool = False

    def visible_topics(self, player: "Player") -> list[str]:
        """Return dialogue topics not suppressed for this player state."""
        return [
            topic for topic in self.dialogue_tree
            if topic not in self.topic_suppress or not self.topic_suppress[topic](player)
        ]

    def respond(self, topic: str) -> str:
        topic = topic.lower().strip()
        for keyword, response in self.dialogue_tree.items():
            if keyword in topic:
                return response
        return f'{self.name} looks at you but says nothing more on that subject.'

    def greet(self, flags: dict) -> str:
        return self.greeting

    def __repr__(self) -> str:
        return f"<Character: {self.name}>"
