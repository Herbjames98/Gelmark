# save_io.py
import os, json

ROOT = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(ROOT, "save_state.json")
LORE_DIR = os.path.join(ROOT, "lore_modules")
MEMORY_FILE = os.path.join(ROOT, "memory_bank.json")

def _fresh_state(defaults_mod) -> dict:
    profile = getattr(defaults_mod, "player_profile", {})
    inv = getattr(defaults_mod, "inventory", {})
    traits = getattr(defaults_mod, "traits", {})
    return {
        "profile": profile,
        "stats": {},
        "inventory": inv,
        "traits": traits,
        "relationships": {},
        "flags": {},
        "position": {"act": 0, "scene": "prologue_start"},
        "scene_counter": 0,
        "scene_cache": {},
        "scene_history": [],
        "story_log": [],
    }

def load_state(defaults_mod) -> dict:
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return _fresh_state(defaults_mod)

def save_state(live: dict) -> None:
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(live, f, indent=2)

def reset_state(defaults_mod, hard: bool = False) -> dict:
    if os.path.exists(SAVE_FILE):
        try: os.remove(SAVE_FILE)
        except Exception: pass
    if hard:
        if os.path.exists(MEMORY_FILE):
            try: os.remove(MEMORY_FILE)
            except Exception: pass
    return _fresh_state(defaults_mod)
