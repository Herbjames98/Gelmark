
# mechanics.py — applies effects to the live save-state dict

from typing import Dict, Any

STAT_CAP = 50

def _bump(d: Dict[str, int], key: str, delta: int) -> None:
    d[key] = int(d.get(key, 0)) + int(delta)

def _cap_stats(stats: Dict[str, int]) -> None:
    for k, v in list(stats.items()):
        try:
            stats[k] = max(0, min(STAT_CAP, int(v)))
        except Exception:
            stats[k] = 0

def apply_effects(state: Dict[str, Any], effects: Dict[str, Any]) -> None:
    if not effects: return
    # Ensure top-level structures
    state.setdefault("stats", {})
    state.setdefault("flags", {})
    state.setdefault("relationships", {})
    state.setdefault("traits", {"active_traits": [], "echoform_traits": [], "hybrid_fusion_traits": []})
    state.setdefault("inventory", {"gold": 0, "key_items": [], "artifacts_relics": [], "equipment": {}, "trait_tokens_drafts": []})

    # 1) Stats
    for k, v in (effects.get("stats") or {}).items():
        _bump(state["stats"], k, int(v))
    _cap_stats(state["stats"])

    # 2) Flags
    for k, v in (effects.get("flags") or {}).items():
        state["flags"][k] = v

    # 3) Relationships
    for k, v in (effects.get("relationships") or {}).items():
        _bump(state["relationships"], k, int(v))

    # 4) Traits add/remove
    for t in (effects.get("traits_add") or []):
        # accept string or dict
        if isinstance(t, str):
            if t not in [x.get("name", x) if isinstance(x, dict) else x for x in state["traits"].get("active_traits", [])]:
                state["traits"]["active_traits"].append({"name": t, "description": ""})
        elif isinstance(t, dict):
            # ensure name present
            name = t.get("name") or t.get("title") or "Unnamed Trait"
            t = dict({"name": name, "description": t.get("description", "")}, **{k:v for k,v in t.items() if k not in ["title"]})
            # dedupe by name
            if all((isinstance(x, dict) and x.get("name") != name) for x in state["traits"]["active_traits"]):
                state["traits"]["active_traits"].append(t)

    for t in (effects.get("traits_remove") or []):
        name = t["name"] if isinstance(t, dict) else str(t)
        state["traits"]["active_traits"] = [x for x in state["traits"]["active_traits"] if (x.get("name") if isinstance(x, dict) else x) != name]

    # 5) Inventory ops
    inv = state["inventory"]
    # Gold
    if "gold" in effects:
        inv["gold"] = int(inv.get("gold", 0)) + int(effects.get("gold", 0))
        if inv["gold"] < 0: inv["gold"] = 0
    # Add/remove key items
    for item in (effects.get("key_items_add") or []):
        if item not in inv.setdefault("key_items", []):
            inv["key_items"].append(item)
    for item in (effects.get("key_items_remove") or []):
        inv.setdefault("key_items", [])
        inv["key_items"] = [x for x in inv["key_items"] if x != item]
    # Artifacts / relics
    for item in (effects.get("artifacts_add") or []):
        if item not in inv.setdefault("artifacts_relics", []):
            inv["artifacts_relics"].append(item)
    for item in (effects.get("artifacts_remove") or []):
        inv.setdefault("artifacts_relics", [])
        inv["artifacts_relics"] = [x for x in inv["artifacts_relics"] if x != item]
    # Equipment (simple slots)
    for slot, val in (effects.get("equip") or {}).items():
        inv.setdefault("equipment", {})
        inv["equipment"][slot] = val
    for slot in (effects.get("unequip") or []):
        inv.setdefault("equipment", {})
        inv["equipment"][slot] = None

    # 6) Companions
    if effects.get("companions_add"):
        state.setdefault("companions", [])
        for c in effects["companions_add"]:
            if isinstance(c, dict):
                names = [x.get("name","") for x in state["companions"] if isinstance(x, dict)]
                if c.get("name") not in names:
                    state["companions"].append(c)
            else:
                state["companions"].append({"name": str(c), "status": "Ally"})

    if effects.get("companions_remove"):
        state.setdefault("companions", [])
        rem = set([c.get("name", c) if isinstance(c, dict) else str(c) for c in effects["companions_remove"]])
        state["companions"] = [x for x in state["companions"] if (x.get("name","") not in rem)]


# --- Leveling system (based on total stat sum) ---
LEVEL_TIERS = [
    (0,   "Novice of the Gel"),
    (20,  "Initiate"),
    (40,  "Wayfarer"),
    (60,  "Echo‑Touched"),
    (80,  "Gelbound"),
    (100, "Chronicle Bearer")
]

def compute_level(stats: Dict[str, int]):
    # Only count numeric, core stats; ignore summary keys like 'Total Stat Points'
    total = 0
    if stats:
        for k, v in stats.items():
            if isinstance(v, (int, float)) and str(k).lower() != 'total stat points':
                total += int(v)
    title = LEVEL_TIERS[0][1]
    current_floor = 0
    next_cap = None
    for cap, name in LEVEL_TIERS:
        if total >= cap:
            current_floor, title = cap, name
        else:
            next_cap = cap
            break
    return {"total": total, "title": title, "current_floor": current_floor, "next_cap": next_cap}

def apply_level_rewards(state: Dict[str, Any]) -> None:
    lvl = compute_level(state.get("stats", {}))
    state.setdefault("flags", {})
    state.setdefault("inventory", {}).setdefault("trait_tokens_drafts", [])
    # If title changed, award a token and set flag so it doesn't repeat
    if state["flags"].get("level_title") != lvl["title"]:
        state["flags"]["level_title"] = lvl["title"]
        # reward: 1 trait token draft
        state["inventory"]["trait_tokens_drafts"].append({"title": f"{lvl['title']} Token"})

    # 7) Level rewards
    apply_level_rewards(state)
