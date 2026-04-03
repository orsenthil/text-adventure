"""Scene: a named place in the Odyssey with story-labeled transitions."""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from object import WorldObject
    from character import Character
    from player import Player


class Transition:
    def __init__(
        self,
        label: str,
        target: str,
        requires_flag: str | None = None,
        sets_flag: str | None = None,
        suppress_if: Callable[["Player"], bool] | None = None,
    ):
        self.label = label
        self.target = target
        self.requires_flag = requires_flag
        self.sets_flag = sets_flag
        # suppress_if(player) -> True means hide this transition from the menu
        self.suppress_if = suppress_if


class Scene:
    def __init__(
        self,
        scene_id: str,
        name: str,
        short_desc: str,
        long_desc: str,
        passage_key: str = "",
    ):
        self.scene_id = scene_id
        self.name = name
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.passage_key = passage_key
        self.transitions: list[Transition] = []
        self.objects: list["WorldObject"] = []
        self.characters: list["Character"] = []
        self.visited: bool = False
        self.state: dict = {}

    def add_transition(
        self,
        label: str,
        target: str,
        requires_flag: str | None = None,
        sets_flag: str | None = None,
        suppress_if: Callable[["Player"], bool] | None = None,
    ) -> None:
        self.transitions.append(Transition(label, target, requires_flag, sets_flag, suppress_if))

    def get_object(self, name: str) -> "WorldObject | None":
        """Find an object by name or alias."""
        name = name.lower().strip()
        for obj in self.objects:
            if name == obj.name.lower() or name in [a.lower() for a in obj.aliases]:
                return obj
        return None

    def get_character(self, name: str) -> "Character | None":
        """Find a character by name or alias."""
        name = name.lower().strip()
        for char in self.characters:
            if name == char.name.lower() or name in [a.lower() for a in char.aliases]:
                return char
        return None

    def remove_object(self, obj: "WorldObject") -> None:
        if obj in self.objects:
            self.objects.remove(obj)
