# This file holds the current state of the player for the Character Sheet page.

player_profile = {
    "name_title": "Askr, Pulse-Bearer of the Fractured Oath",
    "current_arc_act": "Act 3, Chapter 4: The Sightless Hollow",
    "origin_class_lineage": "Human, Time-Sent Heir of GelCap, Echo-Kin Hybrid (Threadcaller / Memorykeeper)",
    "covenant_oath": "Vow to become a sanctuary for the unremembered."
}

stats_overview = {
    "Strength": 13,
    "Dexterity": 0,
    "Insight": 10,
    "Focus": 12,
    "Charisma": 1,
    "Resolve": 0,
    "Spirit": 0,
    "Agility": 0,
    "Willpower": 0,
    "Lore": 0
}

traits = {
    "active_traits": [
        "Oathbraid (Gained from Refusal Spiral vow)",
        "Commandless Grace (Gained from Reliquary of the Unremembered)"
    ],
    "echoform_traits": [
        "Mirrorburst (Awakened in Act 1)"
    ],
    "hybrid_fusion_traits": [
        "Twin Flame Anchor (Caelik Bond)",
        "Scorchbind Core (Caelik Bond)",
        "Pulse Woven (Grace Bond)"
    ],
    "unlocked_vision_threads": [
        "The Blinding Crown's true nature",
        "The Refusal Spiral's purpose"
    ]
}

abilities_techniques = {
    "combat_techniques": [],
    "memory_engine_skills": [
        "Memory Offering (Can offer a memory to a Vault to gain a trait)"
    ],
    "shrine_derived_powers": [
        "Seer's Pulse (#SP) - Ranks narrative decisions."
    ],
    "rituals_invocations": [
        "Vow of the Memorykeeper"
    ]
}

inventory = {
    "artifacts_relics": [
        {
            "name": "Witness Unchosen",
            "origin": "Pacified Blinding Crown",
            "passive_effect": "Grants passive resistance to recursion threats. Can be invoked to nullify a memory attack."
        }
    ],
    "key_items": [
        "Fragmented Keystone (Reacts to shrine resonance)"
    ],
    "consumables": [],
    "equipment": {
        "weapon": "Coreborn Hammer (Currently inert, needs re-syncing)",
        "armor": "Memorybound Cloak (+1 Stealth, detects ambient threads)",
        "accessories": []
    }
}

companions = [
    {
        "name": "G.R.A.C.E.",
        "origin": "Crown AI Fragment, Guardian Threadline Unit",
        "echoform_link_oath_status": "Deeply bonded through shared memory and sacrifice.",
        "current_sync_percent": "115% (Override Dialogue Tier II unlocked)",
        "traits_shared": ["Pulse Woven"],
        "key_shared_events": [
            "Activation at the Refusal Spiral Shrine",
            "Witnessed the Vow of the Memorykeeper",
            "Memoryfire Crucible Trial"
        ]
    },
    {
        "name": "Thjolda",
        "origin": "Former royal shieldbearer, now an exile.",
        "echoform_link_oath_status": "Bond maxed at 100% after 'The Blade Before the Call' trial.",
        "current_sync_percent": "100%",
        "traits_shared": ["Oathburdened Echo (Glimpse)"],
        "key_shared_events": [
            "Stood by during the Blinding Crown pacification.",
            "Memory rewrite trial: 'What She Forged For You'"
        ]
    },
    {
        "name": "Caelik",
        "origin": "Recursion soldier, bearer of the Refused Flame.",
        "echoform_link_oath_status": "Bond maxed at 100% after 'Ash Born Twice' trial.",
        "current_sync_percent": "100%",
        "traits_shared": ["Twin Flame Anchor", "Scorchbind Core", "Flameforward Oath"],
        "key_shared_events": [
            "Defense Shrine Trial: 'The Choice'",
            "Echo combat simulation",
            "Final loyalty trial: 'Ash Born Twice'"
        ]
    }
]

camp_base_upgrades = {
    "memory_crystal_storage": [],
    "shrine_access_levels": [
        "Crucible of Memoryfire (Act 1)",
        "Refusal Spiral Shrine (Act 2)"
    ],
    "training_grounds_unlocked": []
}

codex_unlocks = {
    "memory_lore_entries": [],
    "shrine_data": [],
    "vision_archives": []
}