# save_io.py
import json, os
SAVE_FILE = os.path.join(os.path.dirname(__file__), "save_state.json")

DEFAULTS = {
    "position": {"act": 1, "chapter": 0, "scene": "prologue_start"},
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

def load_state(fallback_state_module, reset=False):
    if not reset and os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Seed from defaults + player_state.py
    seeded = dict(DEFAULTS)
    seeded["stats"] = dict(getattr(fallback_state_module, "stats_overview", {}))
    seeded["traits"] = dict(getattr(fallback_state_module, "traits", {}))
    seeded["companions"] = list(getattr(fallback_state_module, "companions", []))
    seeded["inventory"] = dict(getattr(fallback_state_module, "inventory", {}))
    save_state(seeded)
    return seeded

def save_state(state):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def reset_state(fallback_state_module):
    """Delete save and re-seed at prologue_start."""
    if os.path.exists(SAVE_FILE):
        try:
            os.remove(SAVE_FILE)
        except Exception:
            pass
    return load_state(fallback_state_module, reset=True)
