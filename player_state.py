# player_state.py (Corrected)

player_profile = {
    "Name": "Security Trainee",
    "Current Arc/Act": "Act 1, Chapter 2",
    "Origin / Class / Lineage": "Human, GelCap Guild Employee (Low-Rank Security)",
    "Covenant Oath": None,
    "Vault Keys Secured": None,
    "Major Arc": "The Gelmark Legacy",
    "Arc Rank": 1,
    "Reputation": 0,
    "Class Alignment": "Survivor"
}

stats_overview = {
    "Strength": 5, "Speed": 5, "Dexterity": 5, "Insight": 5,
    "Focus": 5, "Charisma": 5, "Resolve": 5, "Spirit": 5,
    "Agility": 5, "Willpower": 5, "Lore": 5, "Defense": 5, "Endurance": 5,
    "Total Stat Points": 65
}

traits = {
    "active_traits": [
        {
            "name": "Lingual Symbiosis (G.R.A.C.E.)",
            "description": "G.R.A.C.E. has shut down all non-essential functions to act as a living translator. You can understand and be understood by the local populace, but her processing power and assistance are gone.",
            "status": "Active"
        }
    ],
    "echoform_traits": [],
    "hybrid_fusion_traits": []
}

inventory = {
    "gold": 0,
    "artifacts_relics": [],
    "key_items": [],
    "equipment": {
        "weapon": None,
        "armor": {
            "name": "Crude Viking Clothes",
            "description": "Simple, rough-spun clothes and furs scavenged by G.R.A.C.E. to provide a basic disguise and protection from the cold."
        },
        "offhand": None,
        "accessory_1": {
            "name": "Gel-Lined Viking Helmet",
            "description": "A crudely made iron helmet, padded with a strange, shock-absorbent purple gel. It feels strangely familiar."
        },
        "accessory_2": None
    },
    "vault_keys": [],
    "trait_tokens_drafts": []
}

companions = [
    {
        "name": "G.R.A.C.E.",
        "sync": "Minimal",
        "status": "Translation Module Active (Main Systems Shut Down)",
        "description": "Gelcap Robot Assistant for Cognitive Enhancement. A floating, disk-shaped bot that once glowed with soft purple light. She has sacrificed her core functions to provide a translation link, leaving her inert and silent except for the language you now understand."
    }
]