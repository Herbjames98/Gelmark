import streamlit as st

# lore_core.py

"""
This module contains the complete narrative lore and core story elements of the Gelmark interactive saga,
spanning from the prologue to Act 2. It includes companion backstories, shrine significance, Echoform evolution,
and key events from the main vision threads.
"""

# === 🌌 Prologue: The Pulse Unseen ===
prologue = {
    "summary": "In a broken age where memory governs fate, a silent echo awakens within the Spiral Vault. The protagonist, nameless at first, is drawn to an ancient anomaly pulsing at the world's fracture point.",
    "event": "The first contact with the Seer’s Pulse marks the player's awakening. Time blurs. Echoes ripple. The journey begins not with choice, but consequence."
}

# === 🌀 Act 1: Echoes of the Vault ===
act1 = {
    "Shrine_1": {
        "name": "Memoryfire Crucible",
        "unlocks": ["Insight stat synergy", "Vision 1: The Pulse Awakens"],
        "traits": ["Loopborn", "Seer’s Pulse"]
    },
    "Shrine_2": {
        "name": "Fusion Shrine — Grace + Askr",
        "unlocks": ["Fusion with AI Core", "Grace partial awakening"],
        "traits": ["Frozen Moment"]
    },
    "Shrine_3": {
        "name": "Threaded Split Chamber",
        "unlocks": ["Echoform Phase I"],
        "traits": ["Fracture Delay"]
    },
    "Shrine_4": {
        "name": "Vaultside Echoflow",
        "unlocks": ["Memory Offering Path"],
        "traits": ["Selfless Paradox"]
    },
    "Shrine_5": {
        "name": "Sealed Chamber",
        "unlocks": ["Echoform Phase II"],
        "traits": ["Riftbreaker"]
    },
    "visions": [
        "The Pulse Awakens",
        "Grace’s Future Memory Fragment",
        "Broken Spiral Mirror",
        "Vaultside Collapse"
    ],
    "companions": {
        "Caelik": {
            "origin": "Flamebound Knight of Vael-Rith",
            "bond": "Shielded player during Vaultside collapse.",
            "hybrid": "Flame Hybrid Unlocked"
        },
        "Grace": {
            "origin": "AI from the Spiral Observatory — collapsed timeline",
            "bond": "Echo AI fused with Askr Core during Shrine 2",
            "note": "Sentient after Pulse Fusion. Sync: 115%"
        }
    },
    "codex": [
        "The Voice That Waited",
        "What You Could Have Been",
        "Where Memory Becomes Will"
    ]
}

# === 🔮 Act 2: The Spiral Fracture ===
act2 = {
    "summary": "Following the Seer’s Convergence, the group fractures. Grace self-repairs in the Memory Engine, Caelik guards the Inner Core, and Thjolda's oath-mark becomes key to Shrine 6.",
    "Shrine_6": {
        "name": "Runebound Oathmark",
        "unlocks": ["Thjolda vision", "Shrine hybrid unlock"],
        "traits": ["Twin Flame Anchor"]
    },
    "Echoform_II": {
        "unlock": "Post Vaultside Collapse",
        "trigger": "Memory sacrifice and 100% sync with Grace + Caelik",
        "traits": ["Fracture Delay", "Riftbreaker", "Selfless Paradox"]
    },
    "visions": [
        "The Seer’s Convergence",
        "Shrine Reversal Event"
    ],
    "companions": {
        "Thjolda": {
            "origin": "Runeborn Shieldmaiden",
            "bond": "Discovered in Shrine lattice echo",
            "note": "Oathmark pending. Sync: 75%"
        }
    }
}
