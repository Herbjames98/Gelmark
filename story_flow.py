# story_flow.py
# Hand-authored scenes with explicit "to" fallbacks so the game can advance
# even when AI generation is off or fails. You can freely expand this file.

SCENES = {
    "prologue_start": {
        "title": "Awakening in the Ruins",
        "text": (
            "Alarms gutter to embers. The GelCap facility is a ribcage of steel—"
            "smoking, half-collapsed. G.R.A.C.E. flickers at your shoulder, a soft halo "
            "of purple static. The only sign of order is the 'GG' logos stenciled along "
            "the walls, pointing into a dark corridor."
        ),
        "choices": [
            {
                "id": "gg_corridor",
                "label": "Follow the GG logos into the dark corridor",
                "to": "prologue_corridor"
            },
            {
                "id": "scavenge",
                "label": "Scavenge for anything useful",
                "to": "prologue_scavenge",
                "effects": {
                    "inventory": {
                        "gold": 1,
                        "key_items_add": ["Melted ID Tag"]
                    }
                }
            }
        ]
    },

    "prologue_scavenge": {
        "title": "Cold Pockets of Luck",
        "text": (
            "You pick through a drift of ash and shattered housings. A half-melted ID tag "
            "bears your division glyph—unreadable, but proof you existed here. A single coin "
            "glints in the debris. Beyond it, the corridor waits."
        ),
        "choices": [
            {
                "id": "to_corridor",
                "label": "Head into the corridor",
                "to": "prologue_corridor"
            }
        ]
    },

    "prologue_corridor": {
        "title": "The Glitching Directive",
        "text": (
            "The corridor smells of hot plastic and ozone. Emergency paint shows the GG logo "
            "in repeating arrows. At the end: a half-collapsed bulkhead, and beyond it—a pod "
            "like a cracked seed, humming low."
        ),
        "choices": [
            {
                "id": "inspect_pod",
                "label": "Inspect the pod's systems",
                "to": "prologue_pod",
                "effects": {
                    "flags": {"saw_pod": True}
                }
            },
            {
                "id": "steady_grace",
                "label": "Try to steady G.R.A.C.E.",
                "to": "prologue_grace",
                "effects": {
                    "flags": {"grace_steadied": True}
                }
            }
        ]
    },

    "prologue_grace": {
        "title": "Ghost Light",
        "text": (
            "You cup G.R.A.C.E. in both hands. The glow steadies. A thread of voice returns: "
            "'...hazard... temporal displacement... locate... module...' She nudges you toward "
            "the pod—then dims, as if saving the last of herself."
        ),
        "choices": [
            {
                "id": "go_pod",
                "label": "Approach the pod",
                "to": "prologue_pod"
            }
        ]
    },

    "prologue_pod": {
        "title": "Haze Around the Hyper‑Pod",
        "text": (
            "The pod’s shell is glassed and pitted, but alive. A symbol is burned into the side: "
            "GG Hype‑—the rest lost to fire. When you touch the seam, the shell shrinks with a sound "
            "like breath drawn in. A sphere of gel settles into your palm, warm as skin."
        ),
        "choices": [
            {
                "id": "exit_facility",
                "label": "Pocket the sphere and find an exit",
                "to": "prologue_exit",
                "effects": {
                    "flags": {"prologue_done": True},
                    "inventory": {"key_items_add": ["Shrunk Hyper‑Pod"]}
                }
            }
        ]
    },

    "prologue_exit": {
        "title": "Into the Cold",
        "text": (
            "You climb through a ragged breach and into night air. Pines bow under frost; the stars "
            "are unfamiliar. Somewhere beyond the trees, voices carry—chanting, war‑cold. "
            "G.R.A.C.E. whispers, faint and certain: 'Different century.'"
        ),
        "choices": [
            {
                "id": "toward_lights",
                "label": "Head toward the torchlight",
                "to": "prologue_woods"
            }
        ]
    },

    "prologue_woods": {
        "title": "Edge of the Unknown",
        "text": (
            "Snow breaks under your boots. Between trunks you glimpse a wooden palisade, smoke "
            "from cooking fires, the shadow of men in helmets padded with something that gleams—"
            "a purple sheen you recognize too well."
        ),
        "choices": [
            {
                "id": "approach_settlement",
                "label": "Approach the settlement",
                "to": "prologue_approach_settlement"
            }
        ]
    },

    "prologue_approach_settlement": {
        "title": "First Steps Toward the Vikings",
        "text": (
            "Language hums at the edge of hearing as G.R.A.C.E. reroutes her last circuits—"
            "not speech, not yet, but the shape of meaning. The past is waiting."
        ),
        "choices": []
    }
}
