"""Game: main loop, command dispatch, win/lose conditions."""

import shutil
import textwrap
from typing import TYPE_CHECKING

from passages import PassageLibrary
from world import World
from player import Player
from parser import CommandParser
from menu import MenuBuilder

if TYPE_CHECKING:
    from scene import Scene
    from object import WorldObject

MIN_WIDTH = 40
MAX_WIDTH = 100


def _width() -> int:
    """Current wrap width, based on the connected terminal's size."""
    cols = shutil.get_terminal_size(fallback=(72, 24)).columns
    return max(MIN_WIDTH, min(cols - 2, MAX_WIDTH))


def wrap(text: str) -> str:
    """Wrap text to the current terminal width."""
    width = _width()
    paragraphs = text.split("\n")
    wrapped = []
    for p in paragraphs:
        if p.strip():
            wrapped.append(textwrap.fill(p.strip(), width=width))
        else:
            wrapped.append("")
    return "\n".join(wrapped)


def hr() -> str:
    return "─" * _width()


# The storytelling sequence (memory scenes), in order
STORY_SCENES = [
    "memory_lotus",
    "memory_cyclops",
    "memory_aeolus",
    "memory_circe",
    "memory_hades",
    "memory_sirens",
]


class Game:
    def __init__(self, odyssey_path: str = "odyssey.mb.txt"):
        self.passages = PassageLibrary(odyssey_path)
        self.world = World(self.passages)
        self.player = Player(self.world.get_scene("calypso_cave"))
        self.parser = CommandParser()
        self.menu_builder = MenuBuilder()
        self.running = True
        self._current_menu: list[tuple[str, str]] = []
        self._story_index: int = 0
        self._in_story_mode: bool = False
        self._fog_remaining: int = 0
        self._last_character = None  # tracks who was most recently spoken to

    # ---------------------------------------------------------------- display

    def _print(self, text: str) -> None:
        print(wrap(text))

    def _print_scene(self) -> None:
        scene = self.player.current_scene
        print()
        print(hr())
        print(scene.name.upper())
        print(hr())

        if scene.visited:
            self._print(scene.short_desc)
        else:
            self._print(scene.long_desc)
            if scene.passage_key:
                passage = self.passages.format_passage(scene.passage_key, width=_width() - 4)
                if passage:
                    print(passage)
            scene.visited = True

        # Status line
        crew = self.player.crew_count
        print()
        print(f"  Crew: {crew}/12" + (" • " + ", ".join(
            obj.name for obj in self.player.inventory
        ) if self.player.inventory else ""))

    def _print_menu(self) -> None:
        self._current_menu = self.menu_builder.build(
            self.player.current_scene, self.player
        )
        print(self.menu_builder.format_menu(self._current_menu, width=_width() - 2))

    def _clear_screen(self) -> None:
        print("\x1b[2J\x1b[H", end="")

    # ----------------------------------------------------------------- loop

    def run(self) -> None:
        self._clear_screen()
        self._show_intro()
        self._print_scene()
        self._print_menu()

        while self.running:
            try:
                raw = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nFarewell, wanderer.")
                break

            self._clear_screen()

            if not raw:
                self._print_menu()
                continue

            # Resolve numeric/shortcut input via the menu
            resolved = self.menu_builder.resolve(raw, self._current_menu)
            command = resolved if resolved is not None else raw

            # Fog state (Lotus-Eaters)
            if self._fog_remaining > 0:
                self._fog_remaining -= 1
                if self._fog_remaining == 0:
                    print()
                    self._print(
                        "The fog lifts. You remember who you are, and why you are here."
                    )
                else:
                    print()
                    self._print(
                        "You have forgotten why you are here... "
                        "The lotus-flower haze fills your mind."
                    )
                continue

            verb, noun = self.parser.parse(command)
            self._dispatch(verb, noun)

    def _show_intro(self) -> None:
        print()
        print(hr())
        print("  THE ODYSSEY — An Interactive Story")
        print(hr())
        print(wrap(
            "You are Ulysses, King of Ithaca. You survived the Trojan War "
            "ten years ago, but the gods have kept you from reaching home. "
            "For seven years the goddess Calypso has held you on her island. "
            "Now the gods have relented. The sea is before you."
        ))
        print()
        print(wrap(
            "Type a number to choose an action, or type a command freely. "
            "Type [H] for help at any time."
        ))

    # -------------------------------------------------------------- dispatch

    def _dispatch(self, verb: str, noun: str | None) -> None:
        handlers = {
            "look": self._handle_look,
            "examine": self._handle_examine,
            "take": self._handle_take,
            "drop": self._handle_drop,
            "inventory": self._handle_inventory,
            "use": self._handle_use,
            "wear": self._handle_wear,
            "talk": self._handle_talk,
            "ask": self._handle_ask,
            "go": self._handle_go,
            "tell_story": self._handle_tell_story,
            "remember": self._handle_remember,
            "shoot": self._handle_shoot,
            "help": self._handle_help,
            "save": self._handle_save,
            "load": self._handle_load,
            "quit": self._handle_quit,
            "empty": lambda n: None,
            "unknown": self._handle_unknown,
        }
        handler = handlers.get(verb, self._handle_unknown)
        handler(noun)
        self._check_win()

    # -------------------------------------------------- individual handlers

    def _handle_look(self, noun: str | None) -> None:
        scene = self.player.current_scene
        print()
        print(hr())
        print(scene.name.upper())
        print(hr())
        self._print(scene.long_desc)
        if scene.passage_key:
            passage = self.passages.format_passage(scene.passage_key, width=_width() - 4)
            if passage:
                print(passage)
        self._print_menu()

    def _handle_examine(self, noun: str | None) -> None:
        if noun is None:
            self._handle_look(None)
            return
        scene = self.player.current_scene
        obj = scene.get_object(noun) or self.player.has_item(noun)
        if obj:
            print()
            self._print(obj.description)
            self._print_menu()
            return
        char = scene.get_character(noun)
        if char:
            print()
            self._print(char.greeting)
            self._print_menu()
            return
        print()
        self._print(f"You don't see any {noun} here.")
        attempts = self.player.record_attempt()
        self._maybe_hint(attempts)
        self._print_menu()

    def _handle_take(self, noun: str | None) -> None:
        if noun is None:
            print()
            self._print("Take what?")
            self._print_menu()
            return
        scene = self.player.current_scene
        obj = scene.get_object(noun)
        if obj is None:
            print()
            self._print(f"You don't see any {noun} here.")
            attempts = self.player.record_attempt()
            self._maybe_hint(attempts)
            self._print_menu()
            return
        if not obj.takeable:
            print()
            self._print(f"You can't take {obj.name}.")
            self._print_menu()
            return
        self.player.take(obj)
        # Side effects
        if obj.name == "bronze axe":
            self.player.flags["axe_taken"] = True
        print()
        self._print(f"You take {obj.name}.")
        # Always show description on pickup so Examine is not needed
        self._print(obj.description)
        self._print_menu()

    def _handle_drop(self, noun: str | None) -> None:
        if noun is None:
            print()
            self._print("Drop what?")
            self._print_menu()
            return
        obj = self.player.has_item(noun)
        if obj is None:
            print()
            self._print(f"You're not carrying any {noun}.")
            self._print_menu()
            return
        self.player.drop(obj)
        print()
        self._print(f"You set down {obj.name}.")
        self._print_menu()

    def _handle_inventory(self, noun: str | None) -> None:
        print()
        self._print(self.player.inventory_display())
        self._print_menu()

    def _handle_use(self, noun: str | None) -> None:
        if noun is None:
            print()
            self._print("Use what?")
            self._print_menu()
            return

        scene = self.player.current_scene

        # Redirect bow-related use to shoot
        if noun and any(w in noun for w in ["bow", "arrow", "quiver"]):
            self._handle_shoot(noun)
            return

        # Special multi-step interactions
        if scene.scene_id == "memory_cyclops":
            self._use_in_cyclops_scene(noun)
            return
        if scene.scene_id == "memory_circe":
            self._use_in_circe_scene(noun)
            return
        if scene.scene_id == "memory_sirens":
            self._use_in_sirens_scene(noun)
            return
        if scene.scene_id == "memory_lotus":
            if any(w in noun for w in ["lotus", "flower"]):
                self._eat_lotus()
                return

        # General: find object in inventory or scene
        obj = self.player.has_item(noun) or scene.get_object(noun)
        if obj and obj.use_result:
            result = obj.use_result(self)
            print()
            self._print(result)
        elif obj:
            print()
            self._print(f"You're not sure how to use {obj.name} here.")
        else:
            print()
            self._print(f"You don't see any {noun} here.")
        self._print_menu()

    def _use_in_cyclops_scene(self, noun: str) -> None:
        scene = self.player.current_scene
        if any(w in noun for w in ["wine", "wineskin"]):
            wineskin = self.player.has_item("wineskin")
            if wineskin:
                print()
                self._print(
                    "You offer Polyphemus the strong wine of Maron. He drinks — once, twice, three times. "
                    '"Give me more," he bellows, "and tell me your name so I may give you a gift." '
                    '"My name is Nobody," you say. '
                    "He drinks again and crashes to the floor, snoring."
                )
                scene.state["cyclops_drunk"] = True
            else:
                print()
                self._print("You don't have any wine.")
        elif any(w in noun for w in ["stake", "olive", "pole"]):
            if not scene.state.get("cyclops_drunk"):
                print()
                self._print(
                    "Polyphemus is still awake — you cannot get near him with the stake. "
                    "Perhaps there is a way to put him to sleep first."
                )
            else:
                stake = self.player.has_item("sharpened stake")
                if not stake:
                    stake = scene.get_object("sharpened stake")
                if stake:
                    print()
                    self._print(
                        "You heat the point of the stake in the embers until it glows, "
                        "then drive it deep into the Cyclops' eye. "
                        "He screams a scream that shakes the cave. "
                        '"Who did this to you?" the other Cyclopes call from outside. '
                        '"Nobody!" he wails. "Nobody is killing me!" '
                        '"Well, if nobody is hurting you, you must be sick — pray to your father." '
                        "They go away. The Cyclops heaves the boulder aside to let the sheep out at dawn. "
                        "You and your men cling to the bellies of the great rams."
                    )
                    self.player.flags["cyclops_defeated"] = True
                    # Unlock the exit
                    scene.transitions[0].requires_flag = None
                else:
                    print()
                    self._print("You need the sharpened stake.")
        else:
            print()
            self._print(f"You're not sure what to do with {noun} here.")
        self._print_menu()

    def _use_in_circe_scene(self, noun: str) -> None:
        if any(w in noun for w in ["moly", "herb", "flower"]):
            moly = self.player.has_item("moly herb")
            if moly:
                print()
                self._print(
                    "When Circe stirs the drugged cup and touches you with her wand, "
                    "you grip the moly herb and draw your sword. "
                    "The drug has no effect. She steps back in shock. "
                    '"You must be Ulysses," she says. "The god Hermes told me you would come." '
                    "She swears by the gods to do you no harm. "
                    "She restores your men from their pig-shape. "
                    '"Before you sail," she says, "you must visit the land of the dead."'
                )
                self.player.flags["circe_appeased"] = True
            else:
                print()
                self._print("You don't have the moly herb.")
        else:
            print()
            self._print(f"You're not sure what to do with {noun} here.")
        self._print_menu()

    def _use_in_sirens_scene(self, noun: str) -> None:
        scene = self.player.current_scene
        if any(w in noun for w in ["wax", "beeswax"]):
            wax = self.player.has_item("beeswax")
            if wax:
                print()
                self._print(
                    "You knead the beeswax warm between your palms "
                    "and stop the ears of every man in your crew. "
                    "They cannot hear a single note."
                )
                scene.state["crew_protected"] = True
            else:
                print()
                self._print("You don't have any beeswax.")
        elif any(w in noun for w in ["rope", "cord"]):
            if not scene.state.get("crew_protected"):
                print()
                self._print(
                    "Your crew can still hear. If you are tied to the mast "
                    "but your crew can hear the Sirens, they will untie you "
                    "when you beg them to. Protect their ears first."
                )
            else:
                rope = self.player.has_item("rope")
                if rope:
                    print()
                    self._print(
                        "Your crew lashes you to the mast, hands and feet. "
                        "Then the Sirens' voices rise across the water — "
                        "the most beautiful sound you have ever heard. "
                        '"Come to us, Ulysses — we know everything that happened at Troy, '
                        'everything that happens across the wide earth." '
                        "You strain against the ropes, screaming at your crew to release you. "
                        "They row harder. The voices fade. The sea opens out ahead. "
                        "You have passed the Sirens."
                    )
                    passage = self.passages.format_passage("sirens_song", width=_width() - 4)
                    if passage:
                        print(passage)
                    self.player.flags["sirens_passed"] = True
                else:
                    print()
                    self._print("You don't have any rope.")
        else:
            print()
            self._print(f"You're not sure what to do with {noun} here.")
        self._print_menu()

    def _eat_lotus(self) -> None:
        print()
        self._print(
            "You eat the lotus flower. A sweetness floods your mind. "
            "Ithaca... what is Ithaca? Your wife, your son — they are like "
            "a dream you cannot quite remember. There is only this shore, this warmth, this flower."
        )
        self._fog_remaining = 3
        self._print_menu()

    def _handle_wear(self, noun: str | None) -> None:
        if noun is None:
            print()
            self._print("Wear what?")
            self._print_menu()
            return
        obj = self.player.has_item(noun)
        if obj is None:
            obj = self.player.current_scene.get_object(noun)
            if obj and obj.takeable:
                self.player.take(obj)
        if obj is None:
            print()
            self._print(f"You don't see any {noun} here.")
            self._print_menu()
            return
        if "rags" in obj.name.lower() or "disguise" in obj.name.lower():
            self.player.flags["disguise_worn"] = True
            obj.relevant_scenes = []  # don't offer Wear again
            print()
            self._print(
                "You pull on the tattered rags. You look like a weathered old beggar — "
                "no one will see the king of Ithaca behind this disguise."
            )
        else:
            print()
            self._print(f"You put on {obj.name}.")
        self._print_menu()

    def _handle_talk(self, noun: str | None) -> None:
        if noun is None:
            print()
            self._print("Talk to whom?")
            self._print_menu()
            return
        char = self.player.current_scene.get_character(noun)
        if char is None:
            print()
            self._print(f"There is no {noun} here to talk to.")
            self._print_menu()
            return
        print()
        # Context-aware greeting for Circe after appeasement
        if char.name == "Circe" and self.player.flags.get("circe_appeased"):
            self._print(
                'Circe smiles at you — as an ally now, not an enchantress. '
                '"Your men are restored, Ulysses. When you are ready, '
                'sail north to the land of the dead. Speak with Teiresias."'
            )
        else:
            self._print(char.greeting)
        char.greeted = True
        self._last_character = char
        self._print_menu()

    def _handle_ask(self, noun: str | None) -> None:
        """ASK ABOUT <topic> — uses the last character spoken to, or the only one in scene."""
        if noun is None:
            print()
            self._print("Ask about what?")
            self._print_menu()
            return
        scene = self.player.current_scene
        if not scene.characters:
            print()
            self._print("There is no one here to ask.")
            self._print_menu()
            return
        # Use last spoken-to character; fall back to first in scene
        char = self._last_character if self._last_character in scene.characters else scene.characters[0]
        print()
        self._print(char.respond(noun))
        self._print_menu()

    def _handle_go(self, noun: str | None) -> None:
        if noun is None:
            print()
            self._print("Go where?")
            self._print_menu()
            return
        scene = self.player.current_scene
        target_id = noun.lower().strip()
        for t in scene.transitions:
            if t.target == target_id:
                if t.requires_flag and not self.player.flags.get(t.requires_flag, False):
                    print()
                    self._print("You can't do that just yet.")
                    self._print_menu()
                    return
                if t.sets_flag:
                    self.player.flags[t.sets_flag] = True
                target = self.world.get_scene(t.target)
                self.player.move_to(target)
                self._print_scene()
                self._print_menu()
                return
        # Scene ID not matched — maybe player typed a description
        print()
        self._print("You can't go that way from here.")
        self._print_menu()

    def _handle_tell_story(self, noun: str | None) -> None:
        if self.player.current_scene.scene_id != "phaeacia_palace":
            print()
            self._print("There is no one here to tell your story to.")
            self._print_menu()
            return
        if self._story_index >= len(STORY_SCENES):
            print()
            self._print(
                "You have already told King Alcinous everything. "
                "The Phaeacians are ready to take you home."
            )
            self._print_menu()
            return
        print()
        self._print(
            "You take a breath. The hall grows quiet. The torches burn low. "
            "You begin to speak, and the memories come flooding back..."
        )
        next_scene_id = STORY_SCENES[self._story_index]
        next_scene = self.world.get_scene(next_scene_id)
        self.player.move_to(next_scene)
        self._story_index += 1
        self._in_story_mode = True
        self._print_scene()
        self._print_menu()

    def _handle_remember(self, noun: str | None) -> None:
        if not self._in_story_mode:
            print()
            self._print("You are not in a memory right now.")
            self._print_menu()
            return
        print()
        self._print(
            "The memory fades. You are back in the great hall of Alcinous, "
            "the torchlight warm on the faces of the Phaeacians."
        )
        self._in_story_mode = False
        palace = self.world.get_scene("phaeacia_palace")
        self.player.move_to(palace)
        self._print_scene()
        self._print_menu()

    def _handle_shoot(self, noun: str | None) -> None:
        scene = self.player.current_scene
        if scene.scene_id != "palace_hall":
            print()
            self._print("You can't shoot anyone here.")
            self._print_menu()
            return
        bow = self.player.has_item("Odysseus's bow")
        arrows = self.player.has_item("quiver of arrows")
        if not bow:
            print()
            self._print(
                "You need the great bow. It is in the storeroom."
            )
            self._print_menu()
            return
        if not self.player.flags.get("bow_strung"):
            print()
            self._print(
                "The bow is not yet strung. You work the great curve with your hands, "
                "testing it. Then — with the ease of long practice — you string it. "
                "A clear note rings out like a swallow's song. "
                "The hall falls silent."
            )
            self.player.flags["bow_strung"] = True
            # Remove bow from relevant_scenes so only the transition shows
            bow = self.player.has_item("Odysseus's bow")
            if bow:
                bow.relevant_scenes = []
            self._print_menu()
            return
        # Shoot
        if noun and any(w in noun for w in ["antinous", "suitor"]):
            print()
            self._print(
                "You shoot. The arrow flies true through all twelve axe-hafts "
                "and takes Antinous in the throat as he raises his cup to drink. "
                "He falls, the wine and blood mingling on the floor. "
                "The suitors look at each other in confusion — then they see your face, "
                "and the bow in your hands, and they know."
            )
            self.player.flags["arrow_shot"] = True
            self.player.flags["antinous_dead"] = True
        elif noun and "axe" in noun:
            print()
            self._print(
                "You shoot the arrow clean through all twelve axe-hafts. "
                "It is a perfect shot. The hall is silent."
            )
            self.player.flags["arrow_shot"] = True
        else:
            print()
            self._print("Shoot at whom? The suitors are before you.")
        self._print_menu()

    def _handle_help(self, noun: str | None) -> None:
        print()
        print(wrap(
            "You can type a number from the menu, or type commands freely. "
            "Useful commands: LOOK (see where you are), EXAMINE [thing], "
            "TAKE [thing], USE [thing], TALK TO [person], ASK ABOUT [topic], "
            "INVENTORY (what you're carrying), WEAR [item], SHOOT [target], "
            "SAVE, LOAD, QUIT."
        ))
        print(wrap(
            "In the Palace of Alcinous, type TELL STORY to relive your adventures. "
            "In a memory, type REMEMBER to return to the present."
        ))
        self._print_menu()

    def _handle_save(self, noun: str | None) -> None:
        self.player.save()
        print()
        self._print("Your journey has been saved.")
        self._print_menu()

    def _handle_load(self, noun: str | None) -> None:
        import json, os
        filepath = "save.json"
        if not os.path.exists(filepath):
            print()
            self._print("No saved journey found.")
            self._print_menu()
            return
        with open(filepath) as f:
            data = json.load(f)

        # Restore scene
        scene_id = data.get("current_scene", "calypso_cave")
        if scene_id not in self.world.scenes:
            scene_id = "calypso_cave"
        self.player.current_scene = self.world.get_scene(scene_id)

        # Restore flags and crew
        self.player.flags.update(data.get("flags", {}))
        self.player.crew_count = data.get("crew_count", 12)
        self.player.visited_scenes = set(data.get("visited_scenes", []))

        # Restore inventory — find objects by name across all scenes
        obj_registry: dict[str, "WorldObject"] = {}
        for scene in self.world.scenes.values():
            for obj in scene.objects:
                obj_registry[obj.name] = obj
        self.player.inventory = []
        for name in data.get("inventory", []):
            if name in obj_registry:
                obj = obj_registry[name]
                # Remove from its scene so it doesn't appear twice
                for scene in self.world.scenes.values():
                    if obj in scene.objects:
                        scene.objects.remove(obj)
                self.player.inventory.append(obj)

        # Restore story index based on flags
        completed = sum([
            self.player.flags.get("cyclops_defeated", False),
            self.player.flags.get("circe_appeased", False),
            self.player.flags.get("hades_visited", False),
            self.player.flags.get("sirens_passed", False),
        ])
        self._story_index = min(completed + 1, len(STORY_SCENES))

        print()
        self._print("Your journey has been restored.")
        self._print_scene()
        self._print_menu()

    def _handle_quit(self, noun: str | None) -> None:
        print()
        self._print("Farewell, wanderer. Ithaca will wait.")
        self.running = False

    def _handle_unknown(self, noun: str | None) -> None:
        print()
        self._print("I don't understand that. Type [H] for help.")
        attempts = self.player.record_attempt()
        self._maybe_hint(attempts)
        self._print_menu()

    # ---------------------------------------------------------------- hints

    def _maybe_hint(self, attempts: int) -> None:
        if attempts < 5:
            return
        scene = self.player.current_scene
        hints = {
            "calypso_cave": "Calypso seems like someone worth talking to. Ask her about home.",
            "calypso_shore": "You have the bronze axe — examine the raft, or set sail.",
            "memory_cyclops": (
                "You need to deal with Polyphemus before you can escape. "
                "The wineskin and the sharpened stake are your tools."
            ),
            "memory_circe": "The moly herb Hermes gave you will protect you from Circe's magic.",
            "memory_sirens": "Use the beeswax first, then the rope.",
            "eumaeus_hut": "Ask Eumaeus about your disguise, then wear the rags.",
            "palace_hall": "The bow is in the storeroom. Get it, string it, then shoot Antinous.",
        }
        hint = hints.get(scene.scene_id)
        if hint:
            print()
            self._print(f"[Hint: {hint}]")
            self.player.reset_attempts()

    # -------------------------------------------------------------- win check

    def _check_win(self) -> None:
        f = self.player.flags
        # Win via shoot handler flags
        if f.get("arrow_shot") and f.get("antinous_dead"):
            self._show_ending()
            self.running = False
            return
        # Win via transition directly to victory scene
        if self.player.current_scene.scene_id == "palace_victory":
            self.player.flags["arrow_shot"] = True
            self.player.flags["antinous_dead"] = True
            self._show_ending()
            self.running = False

    def _show_ending(self) -> None:
        print()
        print(hr())
        print("  THE RETURN")
        print(hr())
        print()
        self._print(
            "The suitors lie where they fell. The hall is yours again. "
            "Eurycleia goes to fetch Penelope."
        )
        print()
        passage = self.passages.format_passage("penelope_reunion", width=_width() - 4)
        if passage:
            print(passage)
        print()
        self._print(
            "Penelope stands in the doorway. She will not rush forward — "
            "she has been deceived before by men who claimed to be Ulysses. "
            "She sets one last test: she tells the servant to move the bed outside. "
            '"The bed cannot be moved," you say. '
            '"I built it myself, around a great olive tree that still grows through the floor. '
            "No man alive knows that secret but me and you and one handmaid. "
            "That bed has not moved. It cannot move.\""
        )
        print()
        self._print(
            "And then Penelope's knees give way, and she runs to you."
        )
        print()
        crew = self.player.crew_count
        lost = 12 - crew
        if lost == 0:
            self._print("You brought every man home safely.")
        elif lost == 1:
            self._print("You lost one good man on the journey. His name will be remembered.")
        else:
            self._print(
                f"You lost {lost} men on the long road home. "
                "Their names live in the story that is told of you."
            )
        print()
        print(hr())
        self._print(
            '"At last this joy has come to both of us."  — Homer, Odyssey XXIII'
        )
        print(hr())
        print()
