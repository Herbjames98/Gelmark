# --- File: player_state.py ---
# --- File: player_state.py ---
# --- File: player_state.py ---
# --- File: player_state.py ---
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
        "Defense": 7,
        "Endurance": 10
    },
    "traits": {
        "active": [
            { "name": "Flamewrought Vow", "status": "Active" },
            { "name": "Frozen Moment", "status": "Active" },
            { "name": "Momentum Strike", "status": "Active" },
            { "name": "Coreborn", "status": "Active" }
        ],
        "echoform": [
            { "name": "Echo Reflex", "status": "Active" },
            { "name": "Dominion Anchor", "status": "Active" },
            { "name": "Timeline Veil", "status": "Temporarily Deactivated (1 Chapter)" }
        ],
        "fused": [
            { "name": "Ashcore Verdict", "status": "Epic Echo-Shattered Artifact" }
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
        { "name": "G.R.A.C.E.", "sync": "50%", "status": "50% Power, Full Memory (Translation & Instruction Modes Active)" },
        { "name": "Thjolda", "sync": "85%", "status": "Romance path ready Act 4+" },
        { "name": "Grace", "sync": "70%", "status": "Possible Vault Key" },
        { "name": "Caelik", "sync": "80%", "status": "Loyalty Trait unlocked" }
    ]
}