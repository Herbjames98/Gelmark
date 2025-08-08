# storyboard.py
# Canon backbone for The Gelmark — open world with gated beats.
# Import in ai_story.py / play loop to keep canon on track.

from typing import Dict, Any, List, Optional

def _beat(id:str, title:str, act:int, chap:int, order:int,
          triggers:Dict[str,Any]=None, window:int=None,
          set_flags:Dict[str,Any]=None, unlock:List[str]=None,
          sidehooks:List[str]=None, notes:str="") -> Dict[str,Any]:
    return {
        "id": id, "title": title, "act": act, "chapter": chap, "order": int(order),
        "triggers": triggers or {},
        "must_happen_by": ({"scenes_window": window} if window else {}),
        "outcomes": {
            "set_flags": set_flags or {f"beat:{id}": True},
            "unlock_beats": unlock or [],
            "suggest_sidehooks": sidehooks or []
        },
        "notes": notes,
    }

STORY_BEATS: List[Dict[str,Any]] = []

# ===== Prologue =====
STORY_BEATS += [
    _beat("A0C1", "Routine & Rejection", 0, 1, 1, window=2,
          notes="Establish trainee life; G.R.A.C.E. baseline."),
    _beat("A0C2", "The Explosion", 0, 2, 2, window=1,
          notes="Facility destroyed; survival set-piece."),
    _beat("A0C3", "The Hidden Pod", 0, 3, 3, window=2,
          notes="Find Gel Capsule; glitchy G.R.A.C.E."),
    _beat("A0C4", "Time Fracture", 0, 4, 4, window=1,
          notes="Time jump sequence into the past."),
]

# ===== Act 1 — First Steps into the Past =====
STORY_BEATS += [
    _beat("A1C1", "Arrival in the Viking Night", 1, 1, 1,
          notes="Observe gel-lined helmets; stealth tension."),
    _beat("A1C2", "G.R.A.C.E.’s Sacrifice", 1, 2, 2, window=2,
          notes="Translator-only mode; other systems off."),
    _beat("A1C3", "Walk Toward the Camp", 1, 3, 3, window=2,
          set_flags={"prologue_done": True, "beat:A1C3": True},
          notes="End Act 1 stinger."),
]

# ===== Act 2 — Chains of the Forgotten =====
STORY_BEATS += [
    _beat("A2C1", "Ash of Arrival", 2, 1, 1,
          notes="Captured/enslaved to Gæl Mines."),
    _beat("A2C2", "Below the Iron Roots", 2, 2, 2,
          notes="5 core mining tasks; stat training unlocks."),
    _beat("A2C3", "Sparks from the Cold", 2, 3, 3,
          triggers={"stats_min":{"Focus":5}}, window=3,
          notes="Craft makeshift charger; partial GRACE."),
    _beat("A2C4", "Before the Fire Falls", 2, 4, 4,
          window=3, notes="Pakariin first visit; guards depart."),
    _beat("A2C5", "Submission", 2, 5, 5, window=2,
          notes="Chasm Trial; Pakariin return and enslave camp."),
    _beat("A2C6", "The Hunt of the Valking", 2, 6, 6,
          notes="Join bounty order; animal hunts; reputation."),
    _beat("A2C7", "The Whisper of Kings", 2, 7, 7,
          triggers={"stats_min":{"Focus":7}}, window=2,
          notes="G.R.A.C.E. 50% power; big reveal."),
]

# ===== Act 3 — Valley of Whispers =====
STORY_BEATS += [
    _beat("A3C1", "The Sightless Hollow", 3, 1, 1, window=2),
    _beat("A3C2", "Descent Lines", 3, 2, 2, window=3,
          triggers={"location_any":["Valley of Whispers"]}),
    _beat("A3C3", "Mirage Threshold Reprisals", 3, 3, 3,
          triggers={"stats_min":{"Focus":7}, "traits_any":["Mnemonic Warden"]},
          notes="Optional revisit; Focus Tier 2 path."),
    _beat("A3C4", "Vael-Rith: First Door", 3, 4, 4, window=1),
    _beat("A3C5", "Shatterspine Bastion", 3, 5, 5, window=1,
          notes="Defense Tier 1 trial; Dominion Anchor."),
    _beat("A3C6", "The Temporal Flame", 3, 6, 6,
          notes="Choose memory tether (Grace/Thjolda/Self)."),
    _beat("A3C7", "Echo Debt", 3, 7, 7, window=1,
          notes="Relic claims a price; grant Relic Boon."),
]

# ===== Act 4 — The Scarred Plains =====
STORY_BEATS += [
    _beat("A4C1", "Smoke Over Greygrass", 4, 1, 1, window=2),
    _beat("A4C2", "The Cartographer’s Debt", 4, 2, 2,
          triggers={"stats_min":{"Focus":7}, "traits_any":["Echo Reflex"]}, window=4),
    _beat("A4C3", "The Valking Ledger", 4, 3, 3),
    _beat("A4C4", "Furnaces Under Sand", 4, 4, 4),
    _beat("A4C5", "Dominion Parley", 4, 5, 5, window=2),
    _beat("A4C6", "The Sleeping Lineage", 4, 6, 6),
    _beat("A4C7", "The Plains Will Burn", 4, 7, 7, window=1),
]

# ===== Act 5 — Keys and Crowns =====
STORY_BEATS += [
    _beat("A5C1", "Gate of the Fourth", 5, 1, 1,
          triggers={"flags_any":["map_fragments_3"]}),
    _beat("A5C2", "Echo of the Crownless", 5, 2, 2),
    _beat("A5C3", "The Three Proofs", 5, 3, 3, window=3),
    _beat("A5C4", "Tether Confrontation", 5, 4, 4, window=1,
          notes="Grace/Thjolda/Self confrontation."),
    _beat("A5C5", "The Dominion Bargain", 5, 5, 5, window=2),
    _beat("A5C6", "Crown Relay Ignition", 5, 6, 6,
          notes="Pay a cost to reveal final locus."),
    _beat("A5C7", "Who Bears the Signal", 5, 7, 7, window=1),
]

# ===== Act 6 — The Fifth Vault =====
STORY_BEATS += [
    _beat("A6C1", "Approach of the Last Door", 6, 1, 1, window=2),
    _beat("A6C2", "The Archivist Beneath", 6, 2, 2, window=1),
    _beat("A6C3", "Trial of Inheritance", 6, 3, 3, window=2),
    _beat("A6C4", "The Split and the Stitch", 6, 4, 4, window=1),
    _beat("A6C5", "The Gelmark Choice", 6, 5, 5, window=1),
    _beat("A6C6", "Collapse or Continuity", 6, 6, 6, window=1),
    _beat("A6C7", "Epilogue: Ancient Signal", 6, 7, 7, window=1),
]

def _meets_triggers(live:Dict[str,Any], t:Dict[str,Any]) -> bool:
    if not t: return True
    flags = live.get("flags", {}) or {}
    for f in (t.get("flags_all") or []):
        if not flags.get(f): return False
    any_flags = t.get("flags_any") or []
    if any_flags and not any(flags.get(f) for f in any_flags):
        return False
    loc_any = t.get("location_any") or []
    if loc_any:
        loc = (live.get("position") or {}).get("location")
        if loc not in loc_any: return False
    req = (t.get("stats_min") or {})
    stats = live.get("stats", {})
    for k, v in req.items():
        try:
            if int(stats.get(k, 0)) < int(v): return False
        except Exception:
            return False
    if t.get("traits_any"):
        traits = live.get("traits", {}) or {}
        names = { (x.get("name") if isinstance(x,dict) else str(x)) for x in (traits.get("active_traits") or []) }
        if not any(name in names for name in t["traits_any"]):
            return False
    return True

def _beat_done(live:Dict[str,Any], beat_id:str) -> bool:
    return bool((live.get("flags") or {}).get(f"beat:{beat_id}"))

def _canon_order_key(b:Dict[str,Any]):
    return (b["act"], b["chapter"], b["order"])

def next_canonical_beat(live:Dict[str,Any]) -> Optional[Dict[str,Any]]:
    pending = [b for b in sorted(STORY_BEATS, key=_canon_order_key) if not _beat_done(live, b["id"])]
    if not pending: return None
    for b in pending:
        if _meets_triggers(live, b.get("triggers", {})):
            return b
    return pending[0]

def mark_beat_complete(live:Dict[str,Any], beat_id:str) -> None:
    live.setdefault("flags", {})[f"beat:{beat_id}"] = True
