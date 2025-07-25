class PlayerState:
    def __init__(self):
        self.profile = {
            "name_title": "Askr",
            "current_arc_act": "Act 3, Chapter 5",
            "origin_class_lineage": "Human, Black male with black beard",
            "covenant_oath": "I vow to become more than fire or silence… to shelter broken echoes… and carry forgotten names across the void… and keep faith with every memory that still waits to be heard.",
            "vault_keys_secured": "4/5",
            "major_arc": "Legacy Through Echo",
            "arc_rank": 36,
            "reputation": 60,
            "class_alignment": "Echo-Kin Hybrid (Threadcaller / Memorykeeper)"
        }

        self.stats = {
            "Strength": 15, "Speed": 10, "Dexterity": 10, "Insight": 10,
            "Focus": 12, "Charisma": 4, "Resolve": 13, "Spirit": 12,
            "Agility": 10, "Willpower": 13, "Lore": 10, "Defense": 10, "Endurance": 13,
            "total_stat_points": 142
        }

        self.traits = {
            "active": [
                { "name": "Iron Pulse", "description": "A fundamental trait granting a boost to momentum damage." },
                { "name": "Deepcall", "description": "Enhances mental resilience and echo sensitivity in recursion zones." },
                { "name": "Loopborn", "description": "The core recursion trait, allowing retention of memory through splinters and unlocking hybrid fusions." },
                { "name": "Valking Will", "description": "An inherited legacy trait, granting inner fortitude and determination." },
                { "name": "Echo Unbroken", "description": "Provides strong resistance against recursion bleed effects." },
                { "name": "Chrono Pulse", "description": "A rhythm-based trait enhancing recursion and temporal awareness." },
                { "name": "Frozen Authority", "description": "Manifests an ice aura during emotional conflict, boosting strength and intimidation." },
                { "name": "Ashborne Legacy", "description": "A fundamental flame and grief hybrid trait, tied to ancient lineage." },
                { "name": "Refused Flame", "description": "A loyalty tether to Caelik, granting fear immunity and aura buffs." },
                { "name": "Chrono Edge", "description": "Ensures a critical hit on the first strike and maintains Momentum Strike as always active." },
                { "name": "Mnemonic Warden", "description": "Grants abilities for memory-locking and enhanced recall, resisting recursion corruption." },
                { "name": "Flamewrought Vow", "description": "An upgraded trait from Ashborne Legacy, providing bonus Strength when protecting others and allowing recursion purge." },
                { "name": "Frozen Moment", "description": "A technique to briefly halt the flow of localized recursion, freezing enemies or environmental hazards in time; usable once per chapter." },
                { "name": "Flame Without Order", "status": "Echo Shard", "description": "Grants passive immunity to recursion backlash once per act." },
                { "name": "Resilient Mirror", "status": "Echo Shard", "description": "Provides a chance to nullify echo misalignment effects." },
                { "name": "Commandless Grace", "status": "Echo Trait", "description": "Grants +1 Charisma. Allies who witness Askr's stillness may act with initiative, gaining morale bonuses in scene-based actions." },
                { "name": "Oathbraid", "status": "Echo Trait", "description": "Grants +1 Insight permanently. Askr's Vision Threads now imprint emotion onto the world." },
                { "name": "Witness Unchosen", "status": "Echoform Relic", "description": "A crown-memory of past warnings, woven into silence. Grants passive resistance to recursion threats and can nullify a memory attack once per chapter." }
            ],
            "echoform": [
                { "name": "Echo Reflex", "description": "A Tier 2 Focus Echoform passive. Grants bonus dodge or counter once per combat encounter and allows previewing one major decision per chapter." },
                { "name": "Dominion Anchor", "description": "A Tier 1 Defense Echoform trait. Enhances recursion stabilization and protects allies once per chapter." },
                { "name": "Timeline Veil", "status": "Active", "description": "A protective Echoform ability that provides paradox protection, shielding Askr from temporal anomalies; usable once per chapter." }
            ],
            "fused": [
                { "name": "Ashcore Verdict", "status": "Epic Echo-Shattered Artifact (Weapon, Absorbed)", "description": "An artifact formed by fusing the Coreborn trait with the Fractured Flame Sigil. Absorbed into traits/equipment." },
                { "name": "Defiant Momentum", "description": "Provides bonus damage when outnumbered or at low health; ignores the first stagger." },
                { "name": "Glacial Command", "description": "Boosts intimidation and induces fear with a frost aura." },
                { "name": "Time-Sense Bastion", "description": "Increases Focus defense and stutter resistance." },
                { "name": "Echoflame Spiral", "description": "Offers AoE recursion burn and +1 Focus on the first strike." },
                { "name": "Fire Echo Drift", "description": "Grants recursion-burn immunity and synergy with Thjolda." },
                { "name": "Seer’s Pulse", "description": "Auto-vision recursion outcome preview; 'Loop Reversal' once per Act." },
                { "name": "Fracture Delay", "description": "Preemptive time freezing to negate death or phase shifts." },
                { "name": "Riftbreaker", "description": "Critical hit on first strike; breaks recursion shields." },
                { "name": "Phantom Recall", "description": "Auto-dodge one recursion attack; reveals enemy memories." },
                { "name": "Cinder Vow", "description": "Grants recursion resistance; flame loyalty synergy with Caelik." },
                { "name": "Emberfreeze Myriad", "description": "Fire attacks cause chill; grants Strength at low HP." },
                { "name": "Twin Flame Anchor", "description": "Boosts recursion traits with Caelik; allows companion-linked resurrection." },
                { "name": "Temporal Cinder Vow", "description": "Burns flame-based recursion attacks; reflects recursion traits." },
                { "name": "Threadpiercer", "description": "Allows pre-decision intervention and Echo Pulse Strike." },
                { "name": "Pulse Woven", "description": "Grants +1 Focus; overrides hostile dialogue targeting Echo-bonded allies." },
                { "name": "Flameforward Oath", "description": "Grants +1 Focus and first-action priority in flame-aligned scenes." }
            ]
        }

        self.echoform_tiers = {
            "Tier 1 Complete": ["Strength", "Speed", "Defense", "Endurance", "Focus", "Insight"],
            "Tier 2 Unlocked": ["Strength", "Speed", "Defense", "Endurance", "Focus", "Insight"]
        }

        self.inventory = {
            "gold": 6,
            "relics": [
                { "name": "Flame-Echo Mask", "description": "A relic tied to Thjolda's bond and the Temporal Flame." },
                { "name": "Pakariin Glyph", "status": "Suppressed", "description": "A suppressed organic recursion seed." },
                { "name": "Cryo-Mapping Log", "status": "Encrypted", "description": "Encrypted vault trail data." }
            ],
            "key_items": [
                { "name": "Makeshift Charger", "description": "Gel-powered device for reactivating G.R.A.C.E.", "discovered_in": "Act 2, Chapter 3" },
                { "name": "Obsidian Mark", "description": "Mark given by Hunter-Chief Yvorn, initiating the bounty." },
                { "name": "Grace's Codex Prism", "status": "Tier III ready", "description": "Fragment of Grace's knowledge, ready for Codex integration." },
                { "name": "Thjolda's Forge Locket", "status": "Shrine 4 key (pending)", "description": "A key locket from Thjolda for future shrine event." }
            ],
            "equipment": {
                "weapon": {
                    "name": "Sundering Memoryblade",
                    "description": "An echo-reactive longsword scaling with Insight and recursion delay.",
                    "origin": "Acquired after Coreborn Hammer dissolved due to Echoform shift."
                },
                "armor": {
                    "name": "Ashwoven Carapace",
                    "description": "Dominion-forged armor, +2 Endurance in fire zones, -1 Speed elsewhere."
                },
                "offhand": {
                    "name": "Phantom Loop Sigil",
                    "description": "Grants a +5% chance to repeat a nonlethal strike."
                },
                "accessory_1": {
                    "name": "Echo Delay Loop",
                    "description": "Increases recursion immunity window by 1 turn."
                },
                "accessory_2": {
                    "name": "Caelik’s Firebind Ring",
                    "description": "Twin Flame Anchor trait source; linked to Coreborn Hammer."
                }
            },
            "vault_keys": [
                { "name": "Core Receptor Shard", "status": "Secured" },
                { "name": "Dominion Echo Anchor", "status": "Secured" },
                { "name": "Temporal Flame Relic", "status": "Secured" },
                { "name": "The Reflected Blade", "status": "Forged (Prototype Vault Key 4)" },
                { "name": "Living Echo (Grace or Caelik)", "status": "Pending" }
            ],
            "trait_tokens_drafts": [
                { "name": "Mirrored Delay", "type": "Trait Draft", "description": "Draft trait linked to recursion reflection." },
                { "name": "Resonant Mercy", "type": "Trait Draft", "description": "Ashborne-based override/calm synergy." },
                { "name": "Sootroot Fragment", "type": "Flame Echo", "description": "Pending use in shrine fusions." }
            ]
        }

        self.companions = [
            {
                "name": "Grace",
                "sync": "150%",
                "status": "Max Tier I Reached, Codex II complete, Fusion active, Forge Echo Passive acquired.",
                "description": "The Graphical Resonance Architecture Crown Entity (G.R.A.C.E.), an AI-human hybrid deeply connected to Vault architecture."
            },
            {
                "name": "Thjolda",
                "sync": "100%",
                "status": "Max Bond, Shrine-thread resolved, Echo Glimpse forming (Oathburdened Echo).",
                "description": "A fierce Viking warrior with a deep connection to the Temporal Flame."
            },
            {
                "name": "Caelik",
                "sync": "100%",
                "status": "Max Bond, Flame Hybrid complete, Echo integrated.",
                "description": "A loyal recursion soldier and former Crown Herald, bonded with Askr."
            }
        ]

# Export for use
PLAYER_STATE = PlayerState().__dict__
