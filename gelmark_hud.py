# Gelmark Synced Core (Page-Based System)

"""
This unified module uses a page-based structure to manage narrative progression, stat tracking, Echoform evolution, companion arcs, shrine interactions, and systemic branching across acts.
"""

# === 📖 Page Index ===
pages = {
    "Prologue": "page_prologue",
    "Act 1": "page_act1",
    "Act 2": "page_act2",
    "Shrine Threads": "page_shrines",
    "Echoform & Traits": "page_echoform",
    "Companions": "page_companions",
    "Codex Lore": "page_codex",
    "Stats": "page_stats",
    "System Controls": "page_system"
}

# === Modular Imports ===
from lore_modules import prologue, act1, act2

# === 📜 Page: Prologue ===
def page_prologue():
    return prologue.get_data()

# === 📜 Page: Act 1 ===
def page_act1():
    return act1.get_data()

# === 📜 Page: Act 2 ===
def page_act2():
    return act2.get_data()

# === 📜 Page: Shrine Threads ===
def page_shrines():
    return [
        "Shrines act as memory loci tied to stat synergy and trait fusion. Each number reflects a unique narrative gatepoint, not in-world naming.",
        "Shrine 1: Insight & Loopborn | Shrine 2: Fusion + Frozen Moment | Shrine 3: Echoform | Shrine 4: Memory Offering | Shrine 5: Riftbreaker",
        "Shrine 6: Oathmark (Thjolda)"
    ]

# === 📜 Page: Echoform & Traits ===
def page_echoform():
    return {
        "phases": {
            "I": ["Fracture Delay"],
            "II": ["Selfless Paradox", "Riftbreaker"]
        },
        "unlocked_by": "Shrines 3, 5 + Memory Offering",
        "hybrids": ["Grace + Askr", "Flame Hybrid (Caelik)", "Oathmark Hybrid (Pending)"]
    }

# === 📜 Page: Companions ===
def page_companions():
    return {
        "Caelik": {
            "origin": "Flamebound Knight of Vael-Rith",
            "bond": "Shielded player during collapse",
            "sync": "100%",
            "hybrid": "Flame Hybrid"
        },
        "Grace": {
            "origin": "AI from Spiral Observatory",
            "bond": "Fused with Askr Core",
            "sync": "115%",
            "form": "Recovered robot at crash site"
        },
        "Thjolda": {
            "origin": "Runeborn Shieldmaiden",
            "bond": "Shrine lattice echo",
            "sync": "75%"
        }
    }

# === 📜 Page: Codex Lore ===
def page_codex():
    return [
        "The Voice That Waited", "What You Could Have Been", "Where Memory Becomes Will"
    ]

# === 📜 Page: Stats ===
def page_stats():
    return {
        "Insight": 17,
        "Endurance": 12,
        "Will": 14,
        "Focus": 19,
        "Echoform Resonance": 22
    }

# === ⚙️ Page: System Controls ===
def page_system():
    return {
        "Seer’s Pulse": "Enabled",
        "Echoform Memory Rewrites": "Logically Sequenced",
        "Trait Fusions": "Tracking Active",
        "Arc Rank": "Apostate Tier II",
        "Checkpoint": "Shrine 6 (Runebound Oathmark)"
    }
