# --- File: player_state.py ---
# This file holds the current state of the player for the Character Sheet page.

PLAYER_STATE = {
    "profile": {
        "name_title": "Askr",
        "current_arc_act": "Act 3, Chapter 4",
        "origin_class_lineage": "Human, Black male with black beard",
        "covenant_oath": "",
        "vault_keys_secured": "2/5",
        "major_arc": "Legacy Through Echo"
    },
    "stats": {
        "Strength": 8,
        "Speed": 10,
        "Dexterity": 8,
        "Insight": 5,
        "Focus": 7,
        "Charisma": 3,
        "Resolve": 9,
        "Spirit": 5,
        "Agility": 10,
        "Willpower": 9,
        "Lore": 4,
        "Defense": 5,
        "Endurance": 10
    },
    "traits": {
        "active": [
            { "name": "Flamewrought Vow", "status": "Active", "description": "An upgraded trait from Ashborne Legacy. This powerful active trait is unlocked through a deep connection with Thjolda's past and lineage, allowing Askr to tap into a surge of fiery strength and recursion shielding." },
            { "name": "Frozen Moment", "status": "Active", "description": "A technique to briefly halt the flow of localized recursion, freezing enemies or environmental hazards in time." },
            { "name": "Momentum Strike", "status": "Active", "description": "A powerful attack that gains additional force from Askr's continuous movement or successful strikes." },
            { "name": "Coreborn", "status": "Active", "description": "A fundamental trait representing Askr's intrinsic connection to recursion energy, forming the base for powerful Echoform fusions." }
        ],
        "echoform": [
            { "name": "Echo Reflex", "status": "Active", "description": "A Tier 2 Focus Echoform passive. This trait grants Askr a bonus dodge or counter once per combat encounter and allows him to 'preview' one major decision per chapter, offering a glimpse into potential outcomes." },
            { "name": "Dominion Anchor", "status": "Active", "description": "A Tier 1 Defense Echoform trait. Acquired after making a critical choice to protect Thjolda at the Defense Echoform Shrine, this trait enhances Askr's ability to stabilize recursion and resist external influences." },
            { "name": "Timeline Veil", "status": "Temporarily Deactivated (1 Chapter)", "description": "A protective Echoform ability that provides paradox protection, shielding Askr from temporal anomalies. Currently offline due to a deeper insight activation." }
        ],
        "fused": [
            { "name": "Ashcore Verdict", "status": "Epic Echo-Shattered Artifact", "description": "An Epic Echo-Shattered Artifact, formed by fusing the Coreborn trait with the Fractured Flame Sigil. Its glyphs don't etch, they rupture, signifying immense, unstable power rooted in temporal flame." }
        ]
    },
    "inventory": {
        "relics": [],
        "key_items": [
            { "name": "Makeshift Charger", "description": "A crude gel-powered device for reactivating G.R.A.C.E.", "discovered_in": "Act 2, Chapter 3"}
        ],
        "equipment": {
            "weapon": "",
            "armor": "Crude Viking Attire (Gel-Lined Helmet)"
        }
    },
    "companions": [
        { "name": "G.R.A.C.E.", "sync": "115%", "status": "Deeply bonded, Override Dialogue unlocked.", "description": "Gelcap Robot Assistant for Cognitive Enhancement, a floating disk-shaped AI assistant with a soft purple glow, providing guidance and critical information. Her systems are deeply bonded with Askr, and she holds vital memory fragments." },
        { "name": "Thjolda", "sync": "85%", "status": "Romance path ready Act 4+, Strong temporal bond, Echo Key potential confirmed.", "description": "A fierce Viking warrior with a deep connection to the Temporal Flame. Askr's Echo-Tether revealed her past and potential as one of the five Echo Keys, forming a powerful bond." },
        { "name": "Caelik", "sync": "80%", "status": "Loyalty Trait unlocked, Loyalty solidified despite difficult choices.", "description": "A loyal Viking companion whose bond with Askr has deepened through shared trials and difficult decisions, even when faced with Askr's protective choices for others." }
    ]
}