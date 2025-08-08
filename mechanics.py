# mechanics.py
STAT_CAP = 50
THRESHOLDS = list(range(5, 1000, 5))  # total stat thresholds for boss scaling

def apply_effects(state, effects):
    # Stats
    for k, delta in (effects.get("stats") or {}).items():
        curr = state["stats"].get(k, 0)
        state["stats"][k] = max(0, min(STAT_CAP, curr + int(delta)))
    # Flags
    for k, v in (effects.get("flags") or {}).items():
        state.setdefault("flags", {})[k] = v
    # Relationships
    for k, delta in (effects.get("relationships") or {}).items():
        curr = state.setdefault("relationships", {}).get(k, 0)
        state["relationships"][k] = max(0, curr + int(delta))
    # Traits (auto-slot); allow either simple names or bucketed dicts
    for t in (effects.get("traits_add") or []):
        if isinstance(t, dict):
            for bucket, name in t.items():
                state["traits"].setdefault(bucket, [])
                if name not in state["traits"][bucket]:
                    state["traits"][bucket].append(name)
        else:
            state["traits"].setdefault("active_traits", [])
            if t not in state["traits"]["active_traits"]:
                state["traits"]["active_traits"].append(t)

def boss_scale(total_stats):
    idx = 0
    for th in THRESHOLDS:
        if total_stats >= th: idx += 1
        else: break
    return idx
