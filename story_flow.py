# story_flow.py
# Lightweight registry of scenes and choices for the early playable loop.

SCENES = {
    "act1_camp_gate": {
        "title": "At the Viking Camp Gate",
        "text": (
            "Wrapped in crude furs, you approach the palisade. Guards trade glances at your gel-lined helm.\n"
            "G.R.A.C.E. hums weakly, translating in broken phrases."
        ),
        "choices": [
            {
                "id": "parley",
                "label": "Speak calmly and request shelter.",
                "requires": {},
                "effects": {
                    "stats": {"Charisma": 1},
                    "relationships": {"G.R.A.C.E.": 1},
                    "flags": {"met_gate_guard": True}
                },
                "next": "act1_camp_inner"
            },
            {
                "id": "work_mines",
                "label": "Offer labor in exchange for entry (mines).",
                "requires": {},
                "effects": {
                    "stats": {"Strength": 1, "Endurance": 1},
                    "flags": {"mining_quota_started": True}
                },
                "next": "act1_mines_intro"
            }
        ]
    },

    "act1_mines_intro": {
        "title": "The Mines",
        "text": "The air is harsh and metallic. Daily quotas loom, but strength grows with toil.",
        "choices": [
            {
                "id": "train_strength",
                "label": "Train Strength (repeatable)",
                "repeatable": True,
                "effects": {"stats": {"Strength": 1, "Endurance": 1}},
                "next": "act1_mines_intro"
            },
            {
                "id": "proceed",
                "label": "Return to camp",
                "effects": {},
                "next": "act1_camp_inner"
            }
        ]
    },

    "act1_camp_inner": {
        "title": "Inside the Camp",
        "text": (
            "Smoke curls from longhouses. The guard waves you in, wary but curious about the gel in your helm."
        ),
        "choices": [
            {
                "id": "observe",
                "label": "Observe quietly and listen for rumors.",
                "effects": {"stats": {"Insight": 1}},
                "next": "act1_camp_inner"
            },
            {
                "id": "return_gate",
                "label": "Head back toward the gate.",
                "effects": {},
                "next": "act1_camp_gate"
            }
        ]
    }
}
