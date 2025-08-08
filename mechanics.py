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

# ---------- Effects helper ----------
def _ensure(live: dict, path: list, default):
    cur = live
    for key in path[:-1]:
        if key not in cur or not isinstance(cur[key], dict):
            cur[key] = {}
        cur = cur[key]
    cur.setdefault(path[-1], default)
    return cur

def _add_item(lst, item):
    if isinstance(lst, list):
        if item not in lst:
            lst.append(item)

def _remove_item(lst, item):
    if isinstance(lst, list):
        try:
            lst.remove(item)
        except ValueError:
            pass

def apply_effects(live: dict, effects: dict):
    if not effects or not isinstance(effects, dict):
        return
    before = deepcopy(live)

    if "stats" in effects:
        stats = live.setdefault("stats", {})
        for k, dv in effects["stats"].items():
            stats[k] = int(stats.get(k, 0)) + int(dv)

    inv = live.setdefault("inventory", {})
    if "gold" in effects:
        inv["gold"] = int(inv.get("gold", 0)) + int(effects["gold"])
        if inv["gold"] < 0:
            inv["gold"] = 0

    key_items = inv.setdefault("key_items", [])
    for it in effects.get("gain_items", []) or []:
        _add_item(key_items, it)
    for it in effects.get("lose_items", []) or []:
        _remove_item(key_items, it)

    traits = live.setdefault("traits", {})
    active = traits.setdefault("active_traits", [])
    remove_names = set(effects.get("traits_remove", []) or [])
    if remove_names:
        active[:] = [t for t in active if (t.get("name") if isinstance(t, dict) else str(t)) not in remove_names]
    for t in effects.get("traits_add", []) or []:
        tname = t.get("name") if isinstance(t, dict) else str(t)
        if all((x.get("name") if isinstance(x, dict) else str(x)) != tname for x in active):
            active.append(t)

    if "equipment" in effects:
        eq = inv.setdefault("equipment", {})
        for slot, val in (effects.get("equipment") or {}).items():
            eq[slot] = val

    if "relationships" in effects:
        rel = live.setdefault("relationships", {})
        for k, dv in effects["relationships"].items():
            rel[k] = int(rel.get(k, 0)) + int(dv)

    if "flags" in effects:
        fl = live.setdefault("flags", {})
        fl.update({k: v for k, v in effects["flags"].items()})

    pos = live.setdefault("position", {})
    if "act_jump" in effects:
        pos["act"] = int(effects["act_jump"])
    if "scene_id" in effects:
        pos["scene"] = str(effects["scene_id"])

    live["scene_counter"] = int(live.get("scene_counter", 0))
    return before, live
