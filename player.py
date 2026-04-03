"""Player: tracks position, inventory, flags, and crew count."""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scene import Scene
    from object import WorldObject


class Player:
    def __init__(self, start_scene: "Scene"):
        self.current_scene: "Scene" = start_scene
        self.inventory: list["WorldObject"] = []
        self.visited_scenes: set[str] = set()
        self.flags: dict[str, bool] = {
            "cyclops_defeated": False,
            "circe_appeased": False,
            "hades_visited": False,
            "sirens_passed": False,
            "disguise_worn": False,
            "bow_strung": False,
            "arrow_shot": False,
            "antinous_dead": False,
            "raft_built": False,
            "axe_taken": False,
        }
        self.crew_count: int = 12
        # After N failed attempts in the same scene, show a hint
        self._failed_attempts: int = 0
        self._last_scene_id: str = start_scene.scene_id

    def move_to(self, scene: "Scene") -> None:
        if self._last_scene_id != scene.scene_id:
            self._failed_attempts = 0
            self._last_scene_id = scene.scene_id
        self.current_scene = scene
        self.visited_scenes.add(scene.scene_id)

    def take(self, obj: "WorldObject") -> None:
        self.inventory.append(obj)
        self.current_scene.remove_object(obj)

    def drop(self, obj: "WorldObject") -> None:
        if obj in self.inventory:
            self.inventory.remove(obj)
            self.current_scene.objects.append(obj)

    def has_item(self, name: str) -> "WorldObject | None":
        name = name.lower()
        for obj in self.inventory:
            if name == obj.name.lower() or name in [a.lower() for a in obj.aliases]:
                return obj
        return None

    def get_inventory_item(self, name: str) -> "WorldObject | None":
        return self.has_item(name)

    def record_attempt(self) -> int:
        if self._last_scene_id != self.current_scene.scene_id:
            self._failed_attempts = 0
            self._last_scene_id = self.current_scene.scene_id
        self._failed_attempts += 1
        return self._failed_attempts

    def reset_attempts(self) -> None:
        self._failed_attempts = 0

    def save(self, filepath: str = "save.json") -> None:
        data = {
            "current_scene": self.current_scene.scene_id,
            "inventory": [obj.name for obj in self.inventory],
            "visited_scenes": list(self.visited_scenes),
            "flags": self.flags,
            "crew_count": self.crew_count,
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def inventory_display(self) -> str:
        if not self.inventory:
            return "You are carrying nothing."
        items = ", ".join(obj.name for obj in self.inventory)
        return f"You are carrying: {items}."
