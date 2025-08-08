# save_io.py
import json, os
SAVE_FILE = os.path.join(os.path.dirname(__file__), "save_state.json")

DEFAULTS = {
    "position": {"act": 1, "chapter": 2, "scene": "act1_camp_gate"},
    "stats": {},
    "traits": {
        "active_traits": [],
        "echoform_traits": [],
        "hybrid_fusion_traits": []
    },
    "companions": [],
    "inventory": {},
    "flags": {},
    "relationships": {},
    "scene_cache": {}
}

def load_state(fallback_state_module):
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    seeded = dict(DEFAULTS)
    seeded["stats"] = dict(getattr(fallback_state_module, "stats_overview", {}))
    seeded["traits"] = dict(getattr(fallback_state_module, "traits", {}))
    seeded["companions"] = list(getattr(fallback_state_module, "companions", []))
    seeded["inventory"] = dict(getattr(fallback_state_module, "inventory", {}))
    return seeded

def save_state(state):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)