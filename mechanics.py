# mechanics.py
from copy import deepcopy

# ---------- Level math ----------
TIERS = [
    ("Novice of the Gel", 0, 24),
    ("Initiate of Threads", 25, 49),
    ("Echo-Touched", 50, 79),
    ("Shardwalker", 80, 119),
    ("Vaultbound", 120, None),
]

def compute_level(stats: dict):
    if not isinstance(stats, dict):
        stats = {}
    total = sum(int(v) for v in stats.values() if isinstance(v, (int, float)))
    title, floor, cap = TIERS[0][0], 0, TIERS[0][2]
    for t, lo, hi in TIERS:
        if hi is None:
            if total >= lo:
                title, floor, cap = t, lo, None
        elif lo <= total <= hi:
            title, floor, cap = t, lo, hi + 1
            break
    return {"title": title, "total": total, "current_floor": floor, "next_cap": cap}

# ---------- Helpers ----------
def _add_item(lst, item):
    if isinstance(lst, list) and item not in lst:
        lst.append(item)

def _remove_item(lst, item):
    if isinstance(lst, list):
        try:
            lst.remove(item)
        except ValueError:
            pass

# ---------- Effects ----------
def apply_effects(live: dict, effects: dict):
    """
    Apply gameplay effects to the live save dict.

    Supports BOTH schemas:
      A) Flat keys (gold, gain_items, traits_add, flags, relationships, equipment, stats)
      B) Nested inventory block:
         {"inventory": {"gold": 1, "key_items_add": [...], "key_items_remove": [...], "equipment": {...}}}
    """
    if not effects or not isinstance(effects, dict):
        return
    before = deepcopy(live)

    # Stats
    if isinstance(effects.get("stats"), dict):
        stats = live.setdefault("stats", {})
        for k, dv in effects["stats"].items():
            stats[k] = int(stats.get(k, 0)) + int(dv)

    # Ensure inventory scaffolding
    inv = live.setdefault("inventory", {})
    key_items = inv.setdefault("key_items", [])
    eq = inv.setdefault("equipment", {})

    # Flat inventory keys
    if "gold" in effects:
        inv["gold"] = max(0, int(inv.get("gold", 0)) + int(effects["gold"]))
    for it in (effects.get("gain_items") or []):
        _add_item(key_items, it)
    for it in (effects.get("lose_items") or []):
        _remove_item(key_items, it)
    if isinstance(effects.get("equipment"), dict):
        for slot, val in effects["equipment"].items():
            eq[slot] = val

    # Legacy nested inventory block
    if isinstance(effects.get("inventory"), dict):
        inv_fx = effects["inventory"]
        if "gold" in inv_fx:
            inv["gold"] = max(0, int(inv.get("gold", 0)) + int(inv_fx["gold"]))
        for it in (inv_fx.get("key_items_add") or []):
            _add_item(key_items, it)
        for it in (inv_fx.get("key_items_remove") or []):
            _remove_item(key_items, it)
        if isinstance(inv_fx.get("equipment"), dict):
            for slot, val in inv_fx["equipment"].items():
                eq[slot] = val

    # Traits
    traits = live.setdefault("traits", {})
    active = traits.setdefault("active_traits", [])
    remove_names = set(effects.get("traits_remove") or [])
    if remove_names:
        active[:] = [
            t for t in active
            if (t.get("name") if isinstance(t, dict) else str(t)) not in remove_names
        ]
    for t in (effects.get("traits_add") or []):
        name = t.get("name") if isinstance(t, dict) else str(t)
        if all((x.get("name") if isinstance(x, dict) else str(x)) != name for x in active):
            active.append(t)

    # Relationships
    if isinstance(effects.get("relationships"), dict):
        rel = live.setdefault("relationships", {})
        for k, dv in effects["relationships"].items():
            rel[k] = int(rel.get(k, 0)) + int(dv)

    # Flags & position jumps
    if isinstance(effects.get("flags"), dict):
        live.setdefault("flags", {}).update(effects["flags"])
    pos = live.setdefault("position", {})
    if "act_jump" in effects:
        pos["act"] = int(effects["act_jump"])
    if "scene_id" in effects:
        pos["scene"] = str(effects["scene_id"])

    live["scene_counter"] = int(live.get("scene_counter", 0))
    return before, live
