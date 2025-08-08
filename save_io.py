# save_io.py — prologue-safe seeding + hard reset support
import json, os, copy, shutil

SCRIPT_DIR = os.path.dirname(__file__)
SAVE_FILE = os.path.join(SCRIPT_DIR, "save_state.json")
AI_SCENES_FILE = os.path.join(SCRIPT_DIR, "ai_scenes.json")
NARRATIVE_LOG_FILE = os.path.join(SCRIPT_DIR, "narrative_log.txt")
MEMORY_BANK_FILE = os.path.join(SCRIPT_DIR, "memory_bank.json")

# Lore dirs
LORE_DIR = os.path.join(SCRIPT_DIR, "lore_modules")
BASELINE_LORE_DIR = os.path.join(SCRIPT_DIR, "lore_modules_baseline")  # keep pristine copies here

# Minimal, clean prologue defaults (NO Viking gear, NO companions)
DEFAULTS = {
    "position": {"act": 0, "chapter": 1, "scene": "prologue_start"},
    "stats": {},
    "traits": {"active_traits": [], "echoform_traits": [], "hybrid_fusion_traits": []},
    "companions": [],
    "inventory": {
        "gold": 0,
        "key_items": [],
        "artifacts_relics": [],
        "equipment": {"weapon": None, "armor": None, "offhand": None, "accessory_1": None, "accessory_2": None},
        "trait_tokens_drafts": []
    },
    "flags": {},
    "relationships": {},
    "scene_cache": {},
    "story_log": [],
    "scene_history": [],
    "scene_counter": 0
}

def _prologue_seed(fallback_state_module):
    """Seed a fresh game for the prologue.
    We copy *only* stats from player_state.py. Inventory/traits/companions stay clean.
    """
    seeded = copy.deepcopy(DEFAULTS)
    # Import baseline stats from player_state.py if present
    try:
        seeded["stats"] = dict(getattr(fallback_state_module, "stats_overview", {}))
    except Exception:
        pass
    return seeded

def load_state(fallback_state_module, reset=False):
    if not reset and os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Fresh start (prologue)
    seeded = _prologue_seed(fallback_state_module)
    save_state(seeded)
    return seeded

def save_state(state):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def _restore_lore_from_baseline():
    """Overwrite lore_modules with pristine copies from lore_modules_baseline, if available."""
    if os.path.isdir(BASELINE_LORE_DIR):
        if os.path.isdir(LORE_DIR):
            # remove current lore dir completely, then restore
            shutil.rmtree(LORE_DIR, ignore_errors=True)
        shutil.copytree(BASELINE_LORE_DIR, LORE_DIR)

def reset_state(fallback_state_module, hard=False):
    # Remove save + aux files
    for p in [SAVE_FILE, AI_SCENES_FILE, NARRATIVE_LOG_FILE]:
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass
    # Also wipe memory bank on any reset (or only on hard? choose hard-only if you prefer)
    if hard and os.path.exists(MEMORY_BANK_FILE):
        try:
            os.remove(MEMORY_BANK_FILE)
        except Exception:
            pass
    # Restore lore if requested
    if hard:
        _restore_lore_from_baseline()
    return load_state(fallback_state_module, reset=True)
