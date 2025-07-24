# --- File: act3.py ---
# --- File: act3.py ---
# --- File: act3.py ---
# --- File: act3.py ---
# --- File: act3.py ---
# In file: my_gm/lore_modules/act3.py

act3_lore = {
    "summary": "Chapter 4, 'The Sightless Hollow', began with Askr being redirected to the Mirage Threshold Shrine for a Focus Echoform upgrade, unlocking Tier 2 Focus and the 'Echo Reflex' trait, though temporarily deactivating 'Timeline Veil'. An Echo-Tether with Thjolda revealed her potential as an Echo Key and a key vision. Next, Askr journeyed to the Defense Echoform Shrine in Shatterspine Bastion, where a critical decision to save Thjolda resulted in unlocking Tier 1 Defense and the 'Dominion Anchor' trait, while Caelik faded. Relationship bonds with Caelik and Grace deepened through these events. Pursuing a bounty, Askr composed an Echo Message to Thjolda, unlocking the 'Flamewrought Vow' trait after a vision of her past. Intensive training followed, strengthening Loopborn abilities (with a new Codex entry on Grace), and significantly boosting Askr's Defense (to 7), Speed (to 10), and Endurance (remaining at 10) to new thresholds. Combat simulations against powerful foes like the Dominion Vault Warden and The Faultmirror Sovereign honed Askr's skills, culminating in the acquisition of the 'Fractured Flame Sigil' and its fusion with 'Coreborn' into the epic 'Ashcore Verdict' artifact.",
    "major_events": [
        "Start Act 3, Chapter 4: The Sightless Hollow (Objective: Reach Focus Shrine)",
        "Redirected to Mirage Threshold Shrine.",
        "Echoform Focus Tier 2 Unlocked (Echo Reflex trait gained, Timeline Veil temporarily deactivated).",
        "Echo-Tether Initiated with Thjolda (revealing Echo Key potential and Temporal Bond vision).",
        "Defense Echoform Shrine (Shatterspine Bastion) visited.",
        "Defense Trial: The Choice - Saved Thjolda, Caelik faded, unlocked Tier 1 Defense (Dominion Anchor trait).",
        "Pursued Bounty: Flamekeeper’s Remnant (Vision of Thjolda's past, Flamewrought Vow trait upgraded, Echo Message composed).",
        "Loopborn Training Completed (Echo affinity for Grace increased, Grace Fragment Codex unlocked).",
        "Intensive Stat Training (Defense to 7, Speed to 10, Endurance to 10, unlocking Speed Echoform Sync & Echoform Stability thresholds).",
        "Combat Simulation against Dominion Vault Warden (Arc-Rank 30) - Victory (Frozen Moment & Timeline Veil traits used).",
        "Combat Simulation against The Faultmirror Sovereign (Arc-Rank 35) - Victory (Flamewrought Vow & Echo Reflex traits used), Fractured Flame Sigil acquired.",
        "Trait Fusion: Coreborn + Fractured Flame Sigil -> Ashcore Verdict."
    ],
    "companions_bond_status": [
        { "name": "Thjolda", "status": "Romance path ready Act 4+", "sync": "85%", "event": "Echo-Tether, Flamekeeper's Remnant Bounty, Echo Message composed" },
        { "name": "Grace", "status": "Possible Vault Key", "sync": "70%", "event": "Shatterspine Overlook conversation, Loopborn training" },
        { "name": "Caelik", "status": "Loyalty Trait unlocked", "sync": "80%", "event": "Shatterspine Exit conversation, Faded during Defense Trial" }
    ],
    "traits_unlocked": [
        { "name": "Echo Reflex", "type": "Echoform", "description": "Tier 2 Focus Passive. Grants bonus dodge or counter once per encounter. Can 'preview' one major decision per chapter.", "discovered_in": "Act 3, Chapter 4 (Mirage Threshold Shrine)" },
        { "name": "Dominion Anchor", "type": "Echoform", "description": "Tier 1 Defense Trait. Unlocked after saving Thjolda in the Defense Trial.", "discovered_in": "Act 3, Chapter 4 (Defense Echoform Shrine)" },
        { "name": "Flamewrought Vow", "type": "Active", "description": "Upgrade from Ashborne Legacy. Unlocked by pursuing Flamekeeper's Remnant bounty and composing an Echo Message.", "discovered_in": "Act 3, Chapter 4 (Bounty Board)" },
        { "name": "Coreborn", "type": "Active", "description": "A foundational trait, implicitly acquired prior to or during Act 3, used in the fusion of Ashcore Verdict.", "discovered_in": "Act 3, Chapter 4 (Utilized in Fusion)" },
        { "name": "Fractured Flame Sigil", "type": "Component", "description": "A trait component acquired as a reward from defeating The Faultmirror Sovereign simulation, used in the fusion of Ashcore Verdict.", "discovered_in": "Act 3, Chapter 4 (Combat Simulation Reward)" },
        { "name": "Ashcore Verdict", "type": "Fused", "description": "Epic Echo-Shattered Artifact. Fused from Coreborn and Fractured Flame Sigil.", "discovered_in": "Act 3, Chapter 4 (Combat Simulation)" }
    ],
    "shrines_visited": [
        { "name": "Mirage Threshold Shrine", "type": "Focus Echoform Shrine", "location": "Act 3, Chapter 4", "event": "Tier 2 Focus Unlocked" },
        { "name": "Defense Echoform Shrine", "type": "Defense Echoform Shrine", "location": "The Shatterspine Bastion", "event": "Tier 1 Defense Unlocked" }
    ],
    "visions_echo_sequences": [
        { "title": "Temporal Bond — Thjolda", "description": "Askr gains a vision flag related to Thjolda, implying a deeper connection to the Temporal Flame Relic and her role as an Echo Key. Triggered by Echo-Tether.", "discovered_in": "Act 3, Chapter 4 (Echo-Tether)" },
        { "title": "The Last Hearth", "description": "A vision of a young Thjolda before the Flame, seen while pursuing the Flamekeeper's Remnant bounty, revealing her past as a protector.", "discovered_in": "Act 3, Chapter 4 (Flamekeeper's Remnant Bounty)" }
    ],
    "lore_codex_expansions": [
        { "title": "Grace Fragment: Vault Key Compression (Dormant)", "content": "A codex entry unlocked after strengthening Loopborn abilities through training with Grace, hinting at her potential as a Vault Key.", "discovered_in": "Act 3, Chapter 4 (Loopborn Practice)" },
        { "title": "Speed Echoform Sync", "content": "A threshold unlocked after raising Speed to 10, indicating enhanced synergy between Askr's speed and Echoform abilities.", "discovered_in": "Act 3, Chapter 4 (Speed Training)" },
        { "title": "Echoform Stability", "content": "A threshold unlocked after raising Endurance to 10, signifying improved resilience and control over Askr's Echoform manifestations.", "discovered_in": "Act 3, Chapter 4 (Endurance Training)" },
        { "title": "Valley of Whispers", "content": "The initial setting for Act 3, Chapter 4, a haunted valley with fragmented ruins and humming monoliths under an aurora-lit sky, hinting at the Temporal Flame Relic.", "discovered_in": "Act 3, Chapter 4" },
        { "title": "The Faultmirror Sovereign", "content": "An Arc-Rank 35 boss simulated in combat training, defeated by targeting its Mirror Core.", "discovered_in": "Act 3, Chapter 4 (Combat Simulation)" },
        { "title": "Dominion Vault Warden", "content": "An Arc-Rank 30 boss simulated in combat training, defeated by destabilizing its Echoform.", "discovered_in": "Act 3, Chapter 4 (Combat Simulation)" }
    ],
    "timeline_edits": [],
    "key_terms_introduced": [
        "The Sightless Hollow",
        "Valley of Whispers",
        "Mirage Threshold Shrine",
        "Temporal Flame Relic",
        "Shatterspine Bastion",
        "Dominion Vault Warden",
        "The Faultmirror Sovereign",
        "Echo Reflex",
        "Dominion Anchor",
        "Flamewrought Vow",
        "Ashcore Verdict",
        "Fractured Flame Sigil",
        "Coreborn"
    ],
    "locations_realms_visited": [
        "Valley of Whispers",
        "Mirage Threshold Shrine",
        "The Shatterspine Bastion"
    ],
    "faction_threat_encounters": [
        { "name": "Dominion Vault Warden (Simulation)", "status": "Arc-Rank 30 Training Boss", "event": "Defeated in combat simulation" },
        { "name": "The Faultmirror Sovereign (Simulation)", "status": "Arc-Rank 35 Training Boss", "event": "Defeated in combat simulation" }
    ],
    "oaths_rituals_performed": [],
    "artifacts_discovered": [
        { "name": "Ashcore Verdict", "description": "An Epic Echo-Shattered Artifact, formed by fusing Coreborn and Fractured Flame Sigil. Its glyphs rupture rather than etch.", "location": "Act 3, Chapter 4 (Combat Simulation Reward & Fusion)" },
        { "name": "Fractured Flame Sigil", "description": "A trait component acquired as a reward from defeating The Faultmirror Sovereign simulation, used in the fusion of Ashcore Verdict.", "location": "Act 3, Chapter 4 (Combat Simulation Reward)" }
    ],
    "narrative_threads_opened": [
        "The pursuit and nature of the Temporal Flame Relic and its connection to Thjolda's past and potential as an Echo Key.",
        "Grace's potential role as a Vault Key and the significance of 'Vault Key Compression'.",
        "The enduring loyalty and changing dynamics with Caelik and Grace following difficult choices, particularly Caelik's fading.",
        "The implications of the newly acquired 'Ashcore Verdict' artifact."
    ],
    "narrative_threads_closed": []
}