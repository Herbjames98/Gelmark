# save_io.py
import os
import json
from copy import deepcopy
from collections.abc import Mapping

# --- NEW: Deep Update Utility ---
def deep_update(source, overrides):
    """
    Recursively update a dictionary.
    Sub-dictionaries are merged, not overwritten.
    """
    for key, value in overrides.items():
        if isinstance(value, Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source

# --- State Management ---
ROOT = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(ROOT, "save_state.json")
LORE_DIR = os.path.join(ROOT, "lore_modules")
MEMORY_FILE = os.path.join(ROOT, "memory_bank.json")

def _fresh_state(defaults_mod) -> dict:
    """Creates a guaranteed-valid, fresh player state dictionary."""
    profile = deepcopy(getattr(defaults_mod, "player_profile", {}))
    inv = deepcopy(getattr(defaults_mod, "inventory", {}))
    traits = deepcopy(getattr(defaults_mod, "traits", {}))
    
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
    """
    Safely loads the player state using a deep merge.
    This is resilient to old or corrupted save files.
    """
    fresh = _fresh_state(defaults_mod)
    
    if not os.path.exists(SAVE_FILE):
        return fresh

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            saved_state = json.load(f)
        if isinstance(saved_state, dict):
            # Use deep_update to merge states, preserving nested structures
            return deep_update(fresh, saved_state)
    except (json.JSONDecodeError, IOError):
        # If file is corrupted, we just return a fresh state
        pass
        
    return _fresh_state(defaults_mod)

def save_state(live: dict) -> None:
    """Saves the current state to the JSON file."""
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(live, f, indent=2)

def reset_state(defaults_mod, hard: bool = False) -> dict:
    """Resets the game state by deleting old files and creating a new one."""
    if os.path.exists(SAVE_FILE):
        try: os.remove(SAVE_FILE)
        except OSError: pass

    if hard:
        if os.path.exists(MEMORY_FILE):
            try: os.remove(MEMORY_FILE)
            except OSError: pass
    
    new_state = _fresh_state(defaults_mod)
    save_state(new_state)
    return new_state