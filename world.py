"""World: builds all 16 scenes with transitions, objects, and characters."""

from scene import Scene, Transition
from object import WorldObject
from character import Character
from passages import PassageLibrary


class World:
    def __init__(self, passages: PassageLibrary):
        self.passages = passages
        self.scenes: dict[str, Scene] = {}
        self._build()

    def _build(self) -> None:
        self._build_act1()
        self._build_act2()
        self._build_act3()

    # ------------------------------------------------------------------ Act I

    def _build_act1(self) -> None:
        # --- Calypso's Cave ---
        cave = Scene(
            "calypso_cave",
            "Calypso's Island — The Cave",
            "You are in Calypso's vine-draped sea-cave. A loom gleams in firelight.",
            (
                "You stand at the mouth of a vast sea-cave draped in flowering vines. "
                "A fire burns within, filling the air with cedar and sandalwood smoke. "
                "The goddess Calypso sits weaving at her golden loom, singing a beautiful song. "
                "Through the cave's mouth you can see a rocky path leading down to the shore."
            ),
            "calypso_longing",
        )
        cave.add_transition("Walk down to the shore", "calypso_shore")

        hermes_scroll = WorldObject(
            "Hermes' scroll",
            ["scroll", "message", "hermes scroll", "parchment"],
            (
                "A divine message from the gods on Olympus. It says the gods have decreed "
                "that Ulysses must be allowed to return home. Calypso cannot hold him forever."
            ),
            takeable=True,
        )

        axe = WorldObject(
            "bronze axe",
            ["axe", "ax", "bronze ax", "felling axe"],
            (
                "A heavy, sharp-bladed bronze axe — the kind used to fell great trees. "
                "Calypso has left it near the woodpile. It will do for timber."
            ),
            takeable=True,
            use_result=lambda game: (
                "You've already felled the timber and built the raft. "
                "The axe's work here is done."
            ),
            relevant_scenes=[],
        )

        calypso = Character(
            "Calypso",
            ["calypso", "goddess", "nymph"],
            (
                '"Dear Ulysses," the goddess says, looking up from her loom, '
                '"you sit staring at the sea again. Tell me — do you truly wish to leave me, '
                'even knowing what storms await you?"'
            ),
            {
                "home": (
                    '"I know you long for Ithaca," she says, her voice breaking. '
                    '"Your Penelope is mortal. I am a goddess. And yet you weep every day "  '
                    '"on the shore, staring at the sea. The gods have ordered me to let you go. '
                    'Take my axe — fell timber on the hill and build your raft."'
                ),
                "gods": (
                    '"Hermes brought word from Olympus. I cannot defy Zeus himself. '
                    'I will help you build a raft and send you on your way, with a fair wind."'
                ),
                "penelope": (
                    '"She weaves and unravels, weaves and unravels," Calypso says bitterly. '
                    '"Faithful Penelope. But you would choose a mortal woman over a goddess?"'
                ),
                "troy": (
                    '"You fought at Troy for ten years," she says softly. "And now you have '
                    'been here with me for seven more. Seventeen years away from home. '
                    'It is time for you to go."'
                ),
            },
        )

        cave.objects = [hermes_scroll, axe]
        cave.characters = [calypso]
        self.scenes["calypso_cave"] = cave

        # --- Calypso's Shore ---
        shore = Scene(
            "calypso_shore",
            "Calypso's Island — The Shore",
            "The rocky shore where your raft takes shape. The open sea lies west.",
            (
                "The shore is strewn with white pebbles and salt-bleached timber. "
                "Calypso watches from the treeline as you work. "
                "The bronze axe rings against the wood as great trees fall one by one. "
                "In four days you have shaped a raft — oak planks, a mast, a steering oar. "
                "The open sea stretches to the horizon, glittering and immense."
            ),
            "calypso_raft",
        )
        shore.add_transition(
            "Set sail (your raft is ready)",
            "sea_raft",
            requires_flag="axe_taken",
        )
        shore.add_transition("Go back to the cave", "calypso_cave")

        raft = WorldObject(
            "raft",
            ["raft", "boat", "vessel", "timber"],
            (
                "A sturdy raft of oak planks lashed tight with willow withies. "
                "Calypso has given you provisions, water-skins, and a fair wind. "
                "It will carry you across the sea — if the gods permit."
            ),
            takeable=False,
        )

        shore.objects = [raft]
        shore.characters = []
        self.scenes["calypso_shore"] = shore

        # --- The Open Sea ---
        sea = Scene(
            "sea_raft",
            "The Open Sea",
            "Your raft pitches on the grey waves. Storm clouds gather to the north.",
            (
                "For seventeen days you sail, guided by the stars Calypso taught you. "
                "On the eighteenth day, the island of Scheria appears on the horizon — "
                "but at that moment the god Poseidon rises from the deep. "
                "He has not forgotten that you blinded his son, the Cyclops. "
                "Great waves crash over your raft. The mast splinters. You are thrown into the sea."
            ),
            "storm_at_sea",
        )
        sea.add_transition("Swim toward the distant shore", "phaeacia_beach")

        veil = WorldObject(
            "Ino's veil",
            ["veil", "scarf", "divine veil", "ino veil"],
            (
                "A sea-goddess rose from the waves and gave you this veil. "
                '"Bind it beneath your breast," she said, "and you cannot drown." '
                "It shimmers with an otherworldly light."
            ),
            takeable=True,
        )

        sea.objects = [veil]
        self.scenes["sea_raft"] = sea

    # ------------------------------------------------------------------ Act II

    def _build_act2(self) -> None:
        # --- Scheria Beach ---
        beach = Scene(
            "phaeacia_beach",
            "Scheria — The Beach",
            "A sheltered bay on the island of the Phaeacians. You are exhausted.",
            (
                "You crawl out of the surf, naked and salt-crusted, and collapse under "
                "an olive tree where two bushes grow close together like a roof. "
                "When you wake, you hear voices — girls laughing as they do their laundry "
                "by the river. One of them, tall and beautiful as a goddess, "
                "does not run when you emerge from the bushes, grey with sea-brine."
            ),
            "nausicaa_meeting",
        )
        beach.add_transition("Follow Nausicaa toward the city", "phaeacia_palace")

        cloak = WorldObject(
            "Nausicaa's cloak",
            ["cloak", "garment", "nausicaa cloak", "clothing"],
            (
                "A fine woollen cloak that Nausicaa gave you. "
                '"Wash in the river and put this on," she said, "then follow us to my father\'s palace." '
                "It is warm and well-made — the gift of a princess."
            ),
            takeable=True,
        )

        nausicaa = Character(
            "Nausicaa",
            ["nausicaa", "princess", "girl", "young woman"],
            (
                'The princess looks at you without flinching. "You must be some shipwrecked stranger. '
                'This island belongs to the Phaeacians. My father is King Alcinous. '
                'Wash and dress yourself — I will give you clothing — then follow us to the palace."'
            ),
            {
                "father": (
                    '"My father King Alcinous rules the Phaeacians. He is generous to guests. '
                    'Tell him your story and he will help you get home."'
                ),
                "home": (
                    '"Where do you come from? You look like a king, even in your sorry state. '
                    'My father\'s ships can sail anywhere in the world in a single day — '
                    'they will carry you wherever you need to go."'
                ),
                "phaeacians": (
                    '"We are a seafaring people, blessed by the gods. '
                    'Our ships need no rudders — they know the mind of the sailor."'
                ),
            },
        )

        beach.objects = [cloak]
        beach.characters = [nausicaa]
        self.scenes["phaeacia_beach"] = beach

        # --- Palace of Alcinous ---
        palace = Scene(
            "phaeacia_palace",
            "Palace of King Alcinous — The Great Hall",
            "A magnificent palace. King Alcinous sits on his throne, listening.",
            (
                "The palace of Alcinous glitters with gold and silver. "
                "Bronze walls rise to a cornice of deep blue enamel. "
                "The king and queen sit on their thrones surrounded by their nobles. "
                "They have welcomed you, fed you, and given you gifts. "
                "Now Alcinous turns to you with the question every Phaeacian is thinking: "
                '"Stranger, who are you, and how did you come to our shores?"'
            ),
            "alcinous_feast",
        )
        palace.add_transition(
            "Board the Phaeacian ship bound for Ithaca",
            "ithaca_shore",
            requires_flag="sirens_passed",
        )

        chest = WorldObject(
            "chest of gifts",
            ["chest", "gifts", "treasure", "phaeacian gifts"],
            (
                "Bronze tripods, cauldrons, gold, and fine clothing — "
                "the generous gifts of the Phaeacians, stowed in a great chest. "
                "They have asked nothing in return except to hear your story."
            ),
            takeable=False,
        )

        alcinous = Character(
            "King Alcinous",
            ["alcinous", "king", "alcinous king"],
            (
                '"Welcome, stranger. Eat, drink, and rest — then tell us who you are. '
                'My ships have carried men to the ends of the earth. '
                'But first: who are you? What is your story?"'
            ),
            {
                "story": (
                    '"Tell us your name and the tale of your wanderings," Alcinous says, '
                    'leaning forward on his throne. "We have feasted and the hour is right for stories. '
                    'Begin from the beginning — after the fall of Troy."'
                    "\n\n[You take a breath and begin. The memories come flooding back...]"
                    "\n\n>>> Type 'tell story' to relive your journey, starting with the Lotus-Eaters."
                ),
                "home": (
                    '"Name your homeland and I will have you there by morning. '
                    'Our ships are swift as thought and need no guiding hand."'
                ),
                "ship": (
                    '"When you have told your tale, I will have my finest ship '
                    'take you wherever you wish to go, loaded with your gifts."'
                ),
                "name": (
                    '"I am Ulysses, son of Laertes," you say at last, '
                    '"of Ithaca — and perhaps my name has reached even your ears."'
                ),
            },
        )

        palace.objects = [chest]
        palace.characters = [alcinous]
        self.scenes["phaeacia_palace"] = palace

        # --- Memory: Lotus-Eaters ---
        lotus = Scene(
            "memory_lotus",
            "The Land of the Lotus-Eaters",
            "A dreamy shore where your men found sweet oblivion.",
            (
                "After escaping Troy, your fleet made landfall on a strange coast. "
                "You sent three men to explore. They were welcomed by the natives "
                "who gave them the lotus flower to eat. "
                "The three men forgot everything — home, wives, children, ships — "
                "and wished only to stay here forever, eating lotus, "
                "in sweet and perfect forgetfulness."
            ),
            "lotus_warning",
        )
        lotus.add_transition("Drag your men back to the ships by force", "memory_cyclops")

        lotus_flower = WorldObject(
            "lotus flower",
            ["lotus", "flower", "lotus flower"],
            (
                "A pale, beautiful flower with a heady fragrance. "
                "Your men who ate it forgot who they were. "
                "You know better than to taste it."
            ),
            takeable=True,
        )
        lotus.objects = [lotus_flower]
        self.scenes["memory_lotus"] = lotus

        # --- Memory: Cyclops' Cave ---
        cyclops = Scene(
            "memory_cyclops",
            "The Cyclops' Cave",
            "A vast cave reeking of sheep and Cyclops. The great boulder blocks the entrance.",
            (
                "You came to the island of the Cyclopes with twelve of your best men. "
                "You entered this cave — shelves of cheese, pens of lambs — and waited. "
                "Then Polyphemus came home. He blocked the entrance with a boulder "
                "no twenty oxen could shift, and found you huddled in the corner. "
                "He has already eaten two of your men for breakfast. "
                "Two more at dinner. You must act before morning."
            ),
            "polyphemus_blinding",
        )
        cyclops.add_transition(
            "Escape beneath the belly of the great ram",
            "memory_aeolus",
            requires_flag="cyclops_defeated",
        )

        stake = WorldObject(
            "sharpened stake",
            ["stake", "olive stake", "olive wood", "sharp stake", "pole"],
            (
                "A great stake of green olive wood — as long as a ship's mast — "
                "which you found in the cave and sharpened to a point while Polyphemus slept. "
                "It is your only weapon against the giant."
            ),
            takeable=True,
            relevant_scenes=["memory_cyclops"],
        )

        wineskin = WorldObject(
            "wineskin",
            ["wine", "wineskin", "maron wine", "strong wine", "skin of wine"],
            (
                "A skin of extraordinarily strong, sweet wine — a gift from the priest Maron. "
                "One part wine to twenty parts water makes a fine drink. "
                "Undiluted, it would fell a giant."
            ),
            takeable=True,
            relevant_scenes=["memory_cyclops"],
        )

        polyphemus = Character(
            "Polyphemus",
            ["polyphemus", "cyclops", "giant", "one eye"],
            (
                'The Cyclops turns his single terrible eye toward you. '
                '"Who are you, stranger, and where is your ship?" he rumbles. '
                '"My father Neptune will decide what gift I give you."'
            ),
            {
                "name": (
                    '"My name is Nobody," you say. '
                    '"That is what my mother calls me, and my father, and all my friends."'
                ),
                "father": (
                    'The Cyclops laughs. "Then Nobody\'s gift from me shall be this — '
                    'I will eat Nobody last of all." He laughs again and falls into a stupor.'
                ),
            },
        )

        cyclops.objects = [stake, wineskin]
        cyclops.characters = [polyphemus]
        self.scenes["memory_cyclops"] = cyclops

        # --- Memory: Island of the Winds ---
        aeolus = Scene(
            "memory_aeolus",
            "The Island of Aeolus — Keeper of the Winds",
            "A floating island ringed with bronze walls. Aeolus has been a generous host.",
            (
                "Aeolus, keeper of the winds, welcomed you for a whole month. "
                "When you left, he gave you a bag of ox-hide stitched with silver wire, "
                "containing all the winds of storm — leaving only the West Wind free "
                "to carry you home. Ithaca was in sight — you could see the fires on shore — "
                "when your men, thinking the bag held gold, opened it while you slept. "
                "All the winds howled out at once and blew you back here."
            ),
            "bag_of_winds",
        )
        aeolus.add_transition("Sail on toward Circe's island", "memory_circe")

        bag = WorldObject(
            "bag of winds",
            ["bag", "ox-hide bag", "bag of winds", "wind bag"],
            (
                "An ox-hide bag sealed with silver wire — containing all the storm-winds. "
                "It has been opened and emptied. The winds are gone. "
                "Aeolus will help you no more — he thinks you must be cursed by the gods."
            ),
            takeable=False,
        )
        aeolus.objects = [bag]
        self.scenes["memory_aeolus"] = aeolus

        # --- Memory: Circe's Island ---
        circe_scene = Scene(
            "memory_circe",
            "Circe's Island — The Hall",
            "A stone hall in the forest. The enchantress Circe awaits.",
            (
                "Your men found this hall in the forest, heard singing within, and entered. "
                "Circe gave them food and wine mixed with her drugs, "
                "then touched them with her wand — and turned them all into pigs. "
                "Only Eurylochus fled to tell you. "
                "Now you must enter alone. The god Hermes met you on the path "
                "and gave you a herb called moly — its root is black, its flower white as milk — "
                "to protect you from her spells."
            ),
            "circe_enchantment",
        )
        circe_scene.add_transition(
            "Follow Circe's instructions to the land of the dead",
            "memory_hades",
            requires_flag="circe_appeased",
        )

        moly = WorldObject(
            "moly herb",
            ["moly", "herb", "white flower", "divine herb"],
            (
                "The herb moly — black root, white flower — given by Hermes. "
                '"The gods call it moly," he said. "It will protect you from Circe\'s drugs." '
                "Hold it when she raises her wand."
            ),
            takeable=True,
            relevant_scenes=["memory_circe"],
        )

        circe = Character(
            "Circe",
            ["circe", "enchantress", "witch", "goddess"],
            (
                'The beautiful enchantress stirs a golden cup of wine and drugs '
                'and holds it out to you. "Drink, stranger," she says, smiling.'
            ),
            {
                "men": (
                    '"Your men?" Circe leads you to the pig-pen. '
                    'She touches each pig with her wand — and they become men again, '
                    'younger and taller and handsomer than before. '
                    '"I will release them. Stay with me a year, and then I will send you on your way."'
                ),
                "home": (
                    '"Before you sail for Ithaca," Circe says seriously, '
                    '"you must go to the land of the dead. You must speak with Teiresias the prophet. '
                    'Only he can tell you the way home."'
                ),
                "hades": (
                    '"Sail north until you reach the river of Ocean. Beach your ship. '
                    'Dig a trench and pour in honey, wine, and the blood of a black ram. '
                    'The dead will come. Let Teiresias speak first."'
                ),
                "dead": (
                    '"Sail north until you reach the river of Ocean. Beach your ship. '
                    'Dig a trench and pour in honey, wine, and the blood of a black ram. '
                    'The dead will come. Let Teiresias speak first."'
                ),
            },
        )

        circe_scene.objects = [moly]
        circe_scene.characters = [circe]
        self.scenes["memory_circe"] = circe_scene

        # --- Memory: Shore of the Dead ---
        hades_scene = Scene(
            "memory_hades",
            "The Shore of the Dead",
            "A cold, sunless beach at the edge of the world. Shadows drift near.",
            (
                "You have sailed to the end of the world, where the sun never shines. "
                "You dug the trench as Circe instructed and poured the offerings. "
                "The dead came swarming — old comrades, fallen heroes, your own mother. "
                "You held them back with your sword until Teiresias appeared, "
                "drank of the blood, and his eyes grew clear."
            ),
            "tiresias_prophecy",
        )
        hades_scene.add_transition("Return to the world of the living", "memory_sirens")

        sword = WorldObject(
            "bronze sword",
            ["sword", "bronze sword", "blade"],
            (
                "Your sword, drawn to keep the dead at bay until Teiresias could speak. "
                "He told you: Neptune is still angry for the Cyclops' eye. "
                "Keep your hands off the cattle of the Sun-god on your journey home. "
                "In Ithaca, suitors are eating your house — deal with them. "
                "After that, peace."
            ),
            takeable=True,
        )

        teiresias = Character(
            "Teiresias",
            ["teiresias", "prophet", "blind prophet", "shade"],
            (
                'The blind prophet drinks from the trench and his eyes clear. '
                '"Ulysses, son of Laertes. You seek the way home. '
                'Hear me. The god Neptune is still furious — you blinded his son."'
            ),
            {
                "home": (
                    '"You will reach Ithaca, but not easily. '
                    'Whatever you do, do not harm the cattle of the Sun-god Hyperion '
                    'on the island of Thrinacia. If your men touch them, your ship will be destroyed. '
                    'You may survive alone — but it will be long and painful."'
                ),
                "suitors": (
                    '"When you come home you will find arrogant men feasting in your hall, '
                    'courting your wife and wasting your estate. '
                    'You must punish them. After that, plant an oar inland where no man knows the sea, '
                    'and make sacrifice to Neptune. Then you will have peace."'
                ),
                "penelope": (
                    '"Penelope is faithful," the prophet says. "She waits. '
                    'The suitors press her to remarry, but she delays them. "  '
                    '"Be swift when you return — and be cunning."'
                ),
            },
        )

        hades_scene.objects = [sword]
        hades_scene.characters = [teiresias]
        self.scenes["memory_hades"] = hades_scene

        # --- Memory: Sirens' Sea ---
        sirens_scene = Scene(
            "memory_sirens",
            "The Sirens' Sea",
            "A calm, eerie sea. On a low headland, two figures sit among white bones.",
            (
                "Circe warned you: the Sirens sing a song so beautiful "
                "that every sailor who hears it steers toward them and is never seen again. "
                "Their meadow is heaped with the bones of men. "
                "You have beeswax to stop your crew's ears. "
                "But you — you want to hear the song. "
                "For that, you must be tied to the mast."
            ),
            "sirens_song",
        )
        sirens_scene.add_transition(
            "Sail past the Sirens (with crew protected)",
            "phaeacia_palace",
            requires_flag="sirens_passed",
        )

        beeswax = WorldObject(
            "beeswax",
            ["wax", "beeswax", "soft wax"],
            (
                "Soft yellow beeswax, kneaded warm by your hands. "
                "If you stop your crew's ears with this, "
                "they will row past the Sirens without hearing a note."
            ),
            takeable=True,
            relevant_scenes=["memory_sirens"],
        )

        rope = WorldObject(
            "rope",
            ["rope", "cord", "lines", "rigging"],
            (
                "Stout rope from the ship's rigging. "
                "If you are lashed to the mast, you can hear the Sirens and survive — "
                "as long as your crew ignores your orders to untie you."
            ),
            takeable=True,
            relevant_scenes=["memory_sirens"],
        )

        sirens_scene.objects = [beeswax, rope]
        self.scenes["memory_sirens"] = sirens_scene

    # ----------------------------------------------------------------- Act III

    def _build_act3(self) -> None:
        # --- Ithaca Shore ---
        ithaca = Scene(
            "ithaca_shore",
            "Ithaca — Phorcys Harbour",
            "Home at last. The grey cliffs of Ithaca rise above you.",
            (
                "You wake on a beach and do not recognise it — "
                "the goddess Athena has veiled it in mist. "
                "But when the mist clears, you see the cliffs and the harbour of Phorcys, "
                "the great olive tree and the cave of the Naiads — "
                "and you know. You are home. "
                "You fall to your knees and kiss the ground."
            ),
            "ithaca_arrival",
        )
        ithaca.add_transition("Find shelter with the loyal swineherd", "eumaeus_hut")
        self.scenes["ithaca_shore"] = ithaca

        # --- Eumaeus's Hut ---
        eumaeus_hut = Scene(
            "eumaeus_hut",
            "Eumaeus the Swineherd's Hut",
            "A rough hut in the hills. Eumaeus has welcomed you warmly.",
            (
                "The swineherd Eumaeus does not know who you are — Athena has disguised you "
                "as an old beggar — but he welcomes you like a lord, "
                "killing a fat pig and sharing his meal. "
                '"Strangers come from the gods," he says. "I cannot turn away a wanderer." '
                "He tells you about the suitors eating your estate — "
                "and about his hope that Ulysses might still return."
            ),
            "swineherd_welcome",
        )
        eumaeus_hut.add_transition(
            "Go to the palace in disguise",
            "palace_hall",
            requires_flag="disguise_worn",
        )

        rags = WorldObject(
            "beggar's rags",
            ["rags", "disguise", "beggar rags", "old clothes", "tattered clothes"],
            (
                "Worn, tattered clothes that make you look like an old wandering beggar. "
                "Athena suggested this disguise — in the palace, no one will recognise "
                "the great Ulysses behind these rags."
            ),
            takeable=True,
            relevant_scenes=["eumaeus_hut", "ithaca_shore"],
            menu_label="Wear",
            menu_command="wear",
        )

        eumaeus = Character(
            "Eumaeus",
            ["eumaeus", "swineherd", "old man"],
            (
                '"Sit down, stranger, eat something. I will kill a pig — '
                'a poor man\'s feast is the best I can offer. '
                'Strangers are sent by Zeus. I will not dishonour him."'
            ),
            {
                "ulysses": (
                    '"Ah, my master Ulysses!" the swineherd sighs. '
                    '"I believe he still lives, somewhere on the sea. '
                    'But the suitors waste his house and insult his wife. '
                    'It is a shame to the gods."'
                ),
                "suitors": (
                    '"They have been here three years," Eumaeus says bitterly. '
                    '"Eating the cattle, drinking the wine, pressing Penelope to remarry. '
                    'She delays them with her weaving — but she cannot hold out forever."'
                ),
                "penelope": (
                    '"She is a good woman, my mistress," he says. "She weaves all day '
                    'and unravels it by night — a burial shroud, she says, for old Laertes. '
                    'The suitors have not caught on yet."'
                ),
                "disguise": (
                    '"If you want to enter the palace without trouble," '
                    'Eumaeus says, looking at your fine bearing, "you\'d best dress as a beggar. '
                    'Put on those rags in the corner — then the suitors won\'t bother with you."'
                ),
            },
            topic_suppress={
                "disguise": lambda p: p.flags.get("disguise_worn", False),
            },
        )

        eumaeus_hut.objects = [rags]
        eumaeus_hut.characters = [eumaeus]
        self.scenes["eumaeus_hut"] = eumaeus_hut

        # --- The Great Hall ---
        hall = Scene(
            "palace_hall",
            "The Palace of Ulysses — The Great Hall",
            "The great hall. Suitors lounge everywhere, eating your cattle.",
            (
                "The hall is full of insolent men eating, drinking, and laughing. "
                "They hardly notice you — just another wandering beggar. "
                "You can see Penelope at the far end, beautiful and grave. "
                "Your son Telemachus is there too, watching you. "
                "The great bow of Ulysses hangs on the wall — "
                "Penelope has announced a contest: whoever strings the bow "
                "and shoots through twelve axe-hafts wins her hand. "
                "The storeroom where the bow is kept lies at the back."
            ),
            "suitors_feast",
        )
        hall.add_transition(
            "Slip into the storeroom",
            "palace_storeroom",
            suppress_if=lambda p: p.has_item("Odysseus's bow") is not None,
        )
        hall.add_transition(
            "String the bow and shoot through the axes",
            "palace_victory",
            requires_flag="bow_strung",
        )

        penelope = Character(
            "Penelope",
            ["penelope", "queen", "wife"],
            (
                "Penelope looks through you as if you are not there — "
                "she cannot see her husband behind the beggar's rags. "
                '"Stranger," she says quietly, "have you heard anything of Ulysses? '
                'Any word at all of where he might be?"'
            ),
            {
                "husband": (
                    '"I will tell you this," you say carefully. '
                    '"He is alive, and not far away. He will be home before this month is out."'
                    '\nPenelope\'s eyes fill with tears. "Every stranger says this," she whispers. '
                    '"I have learned not to hope."'
                ),
                "contest": (
                    '"I have set the suitors a task," she says. '
                    '"The great bow of Ulysses — whoever can string it and shoot through '
                    'twelve axes as he used to do — I will marry that man." '
                    "Her eyes go flat. \"None of them can even bend it.\""
                ),
                "weaving": (
                    '"I told them I would choose when I finished weaving '
                    'a burial shroud for my father-in-law Laertes," she says. '
                    '"I wove by day and unravelled by night. They found out after three years."'
                ),
            },
        )

        antinous = Character(
            "Antinous",
            ["antinous", "suitor", "lead suitor"],
            (
                'The handsomest and most insolent of the suitors looks at you with contempt. '
                '"Get out of my way, old beggar. This hall is not for your kind."'
            ),
            {
                "bow": (
                    '"You want to try the bow?" Antinous laughs. '
                    '"An old beggar try the bow of Ulysses? '
                    'You can barely stand upright. Get away from it."'
                ),
                "ithaca": (
                    '"Ithaca belongs to whoever has the strength to hold it," '
                    'Antinous says carelessly. '
                    '"Ulysses is twenty years gone. His house is ours now."'
                ),
            },
            topic_suppress={
                "bow": lambda p: p.has_item("Odysseus's bow") is not None,
                "ithaca": lambda p: p.has_item("Odysseus's bow") is not None,
            },
        )

        hall.characters = [penelope, antinous]
        hall.objects = []
        self.scenes["palace_hall"] = hall

        # --- The Storeroom ---
        storeroom = Scene(
            "palace_storeroom",
            "The Palace Storeroom",
            "A quiet storeroom smelling of cedar oil and old bronze.",
            (
                "The storeroom is cool and dark, smelling of cedar oil and polished bronze. "
                "Here hang the weapons of Ulysses — spears, helmets, shields. "
                "And there, on its peg, is the great bow. "
                "It is strung with a twisted cord that gleams. "
                "Beside it stands a quiver of bronze-tipped arrows. "
                "Penelope's handmaid Eurycleia has unlocked the door for you."
            ),
            "bow_of_odysseus",
        )
        storeroom.add_transition("Return to the great hall", "palace_hall")

        bow = WorldObject(
            "Odysseus's bow",
            ["bow", "great bow", "ulysses bow", "odysseus bow", "the bow"],
            (
                "The great horn bow of Ulysses — a gift from the hero Iphitus long ago. "
                "It has not been strung since its master left for Troy. "
                "None of the suitors have been able to bend it. "
                "But you remember every knot."
            ),
            takeable=True,
            relevant_scenes=["palace_hall"],
            menu_label="Shoot",
            menu_command="shoot antinous",
        )

        arrows = WorldObject(
            "quiver of arrows",
            ["arrows", "quiver", "bronze arrows", "arrow"],
            (
                "A quiver of bronze-tipped arrows, ready to fly. "
                "One will do the work."
            ),
            takeable=True,
            relevant_scenes=[],  # bow entry covers shooting; no separate arrows option
        )

        storeroom.objects = [bow, arrows]
        self.scenes["palace_storeroom"] = storeroom

        # --- Victory ---
        victory = Scene(
            "palace_victory",
            "The Great Hall — After the Battle",
            "The hall is silent. The suitors lie where they fell.",
            (
                "The great hall is still. "
                "The last suitor fell before your arrows ran out. "
                "The doors are open, the smoke clearing. "
                "Eurycleia goes to fetch Penelope. "
                "Your faithful wife stands in the doorway, studying you — "
                "not quite believing, not quite daring to hope. "
                "She sets one final test."
            ),
            "penelope_reunion",
        )
        self.scenes["palace_victory"] = victory

    def get_scene(self, scene_id: str) -> Scene:
        return self.scenes[scene_id]
