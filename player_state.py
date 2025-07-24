# --- File: player_state.py ---
# This file holds the current state of the player for the Character Sheet page.

PLAYER_STATE = {
    "profile": {
        "name_title": "Viking Conscript (Gæl Mines)",
        "current_arc_act": "Act 2, Chains of the Forgotten",
        "origin_class_lineage": "Human, GelCap Guild Security Trainee",
        "covenant_oath": ""
    },
    "stats": {
        "Strength": 8, "Dexterity": 8, "Insight": 5,
        "Focus": 7, "Charisma": 3, "Resolve": 9,
        "Spirit": 5, "Agility": 8, "Willpower": 9, "Lore": 4
    },
    "traits": {
        "active": [],
        "echoform": [],
        "fused": []
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
        { "name": "G.R.A.C.E.", "sync": "50%", "status": "50% Power, Full Memory (Translation & Instruction Modes Active)" }
    ]
}