"""MenuBuilder: generates a numbered action list from the current scene and player state."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scene import Scene
    from player import Player


class MenuBuilder:
    # Single-letter shortcuts always shown at the bottom
    SHORTCUTS = [
        ("I", "inventory", "Inventory"),
        ("H", "help", "Help"),
        ("S", "save", "Save"),
        ("Q", "quit", "Quit"),
    ]

    def build(self, scene: "Scene", player: "Player") -> list[tuple[str, str]]:
        """
        Return a list of (display_label, command_string) pairs.
        Numbered items come first, then single-letter shortcuts.
        """
        entries: list[tuple[str, str]] = []

        # 1. Story transitions (move to next scene)
        for t in scene.transitions:
            if t.requires_flag and not player.flags.get(t.requires_flag, False):
                continue
            if t.suppress_if and t.suppress_if(player):
                continue
            entries.append((t.label, f"go {t.target}"))

        # 2. Objects in scene
        for obj in scene.objects:
            if obj.takeable:
                entries.append((f"Take {obj.name}", f"take {obj.name}"))
            else:
                entries.append((f"Examine {obj.name}", f"examine {obj.name}"))

        # 3. Characters in scene
        for char in scene.characters:
            if not char.greeted:
                entries.append((f"Talk to {char.name}", f"talk to {char.name}"))
            else:
                for topic in char.visible_topics(player):
                    label = f"Ask {char.name} about {topic}"
                    entries.append((label, f"ask about {topic}"))

        # 4. Relevant inventory items
        for obj in player.inventory:
            if scene.scene_id in obj.relevant_scenes:
                entries.append(
                    (f"{obj.menu_label} {obj.name}", f"{obj.menu_command} {obj.name}")
                )

        return entries

    def format_menu(self, entries: list[tuple[str, str]], width: int = 44) -> str:
        """Return the formatted menu string ready to print."""
        lines = ["", "What do you do?"]
        for i, (label, _cmd) in enumerate(entries, start=1):
            lines.append(f"  [{i}] {label}")

        # Separator then shortcuts
        lines.append("  " + "─" * width)
        shortcuts = [f"[{k}] {name}" for k, _cmd, name in self.SHORTCUTS]
        lines.append(self._pack_shortcuts(shortcuts, width))
        lines.append("")
        return "\n".join(lines)

    def _pack_shortcuts(self, shortcuts: list[str], width: int) -> str:
        """Join shortcut labels, wrapping onto extra lines if they overflow width."""
        rows: list[str] = []
        current = "  "
        for shortcut in shortcuts:
            candidate = current + ("   " if current.strip() else "") + shortcut
            if len(candidate) > width + 2 and current.strip():
                rows.append(current)
                current = "  " + shortcut
            else:
                current = candidate
        rows.append(current)
        return "\n".join(rows)

    def resolve(self, raw: str, entries: list[tuple[str, str]]) -> str | None:
        """
        If raw is a number or a shortcut letter, return the corresponding
        command string. Otherwise return None (caller handles free text).
        """
        raw = raw.strip()

        # Single-letter shortcuts
        if len(raw) == 1 and raw.upper() in {k for k, _, _ in self.SHORTCUTS}:
            for k, cmd, _ in self.SHORTCUTS:
                if raw.upper() == k:
                    return cmd

        # Numeric selection
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(entries):
                return entries[idx][1]

        return None
