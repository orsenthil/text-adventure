"""WorldObject: a thing in the world that can be examined, taken, or used."""

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class WorldObject:
    def __init__(
        self,
        name: str,
        aliases: list[str],
        description: str,
        takeable: bool = True,
        use_result: Callable | None = None,
        relevant_scenes: list[str] | None = None,
        menu_label: str = "Use",
        menu_command: str = "use",
    ):
        self.name = name
        self.aliases = aliases
        self.description = description
        self.takeable = takeable
        self.use_result = use_result
        self.relevant_scenes: list[str] = relevant_scenes or []
        # Override the menu verb for this object (e.g. "Wear" / "wear")
        self.menu_label = menu_label
        self.menu_command = menu_command

    def __repr__(self) -> str:
        return f"<WorldObject: {self.name}>"
