import streamlit as st
import datetime

# --- Title and Metadata ---
st.set_page_config(page_title="Gelmark HUD v2", layout="wide")
st.title("🌌 Gelmark HUD — Rebuild Edition")

# --- Core Player Stats ---
st.sidebar.header("Player Core")
st.sidebar.text("Arc Rank: Pulsebearer — Spiral Fracture")
st.sidebar.text("Current Location: Vael-Rith Inner Core")
st.sidebar.text("Visions Unlocked: 6")
st.sidebar.text("Shrines Visited: 5")
st.sidebar.text("Echoform Phase: II")

# --- Player Stats ---
st.sidebar.markdown("### Stat Overview")
st.sidebar.text("Strength: 12")
st.sidebar.text("Focus: 11")
st.sidebar.text("Speed: 10")
st.sidebar.text("Defense: 11")
st.sidebar.text("Insight: 9 (T2 Override)")
st.sidebar.text("Endurance: 12")
st.sidebar.text("Total Stat Points: 65")

# --- Companion Status ---
st.sidebar.markdown("### Companions")
st.sidebar.text("Caelik ⚔️  | Sync: 100% — Flame Hybrid Unlocked")
st.sidebar.text("Grace  🔮 | Sync: 115% — AI Core Tier II Dialogue Active")
st.sidebar.text("Thjolda 🛡️ | Sync: 75% — Shrine Thread Pending")
st.sidebar.text("? ? ?      🌀 | Sync: -- — Unknown Echo")

# --- Seer's Pulse Interface ---
st.header("🔍 Seer's Pulse — Choice Ranking")
choice = st.text_input("Enter a decision or action to rank:", "Offer memory fragment to Shrine Flame")
if st.button("Rank Seer's Pulse"):
    st.success("Seer's Pulse Rank: 3 — Resonant Offering. Outcome: Unlocks hybrid fusion + vision thread.")

# --- Trait Panel ---
st.header("💠 Trait Inventory")
trait_cols = st.columns(4)
traits = [
    ("Grace + Askr Fusion (Locked)", "Dormant until Shrine 2 complete"),
    ("Loopborn", "Hybrid Trait"),
    ("Seer’s Pulse", "Hybrid Trait"),
    ("Fracture Delay", "Hybrid Trait"),
    ("Riftbreaker", "Hybrid Trait"),
    ("Phantom Recall", "Hybrid Trait"),
    ("Frozen Moment", "Hybrid Trait"),
    ("Scorchbind Core", "Hybrid Trait"),
    ("Twin Flame Anchor", "Hybrid Trait"),
    ("Temporal Cinder Vow", "Hybrid Trait"),
    ("Threadpiercer", "Hybrid Trait"),
    ("Selfless Paradox", "Echo Trait – Sacrifice shrine memory to preserve another")
]
for i, (name, desc) in enumerate(traits):
    with trait_cols[i % 4]:
        st.subheader(name)
        st.caption(desc)

# --- Shrine Log ---
st.header("🗺️ Shrines Visited")
st.markdown("""
- **Shrine 1** — Memoryfire Crucible (Insight/Fusion Unlock)
- **Shrine 2** — Grace + Askr Fusion (Pending Completion)
- **Shrine 3** — Echoform Thread Split (Vision Lock)
- **Shrine 4** — Vaultside Echoflow (Memory Offering)
- **Shrine 5** — Sealed Chamber — Locked. Sync 100% and Vision Override required.
""")

# --- Companion Logs ---
st.header("🤝 Companion History")
st.markdown("""
**Grace** — Echo AI from the future. Recovered in Shrine 2. Fusion initiated via Flowbinding and Askr core. Fully sentient, voice-reactive. Sync: 115%.

**Caelik** — Swordbound Guardian. Loyal to shrine protocol. Shielded player during Vaultside collapse. Flame Hybrid unlocked. Sync: 100%.

**Thjolda** — Runeborn Shieldmaiden. Found in shrine lattice echo. Oathmark fusion pending. Sync: 75%.
""")

# --- Vision Recap ---
st.header("🔮 Vision Archive")
st.markdown("""
- **Vision 1:** The Pulse Awakens
- **Vision 2:** Grace’s Future Memory Fragment
- **Vision 3:** Broken Spiral Mirror
- **Vision 4:** Vaultside Collapse
- **Vision 5:** The Seer’s Convergence
- **Vision 6:** Shrine Reversal Event
""")

# --- Codex & Memory Status ---
st.header("📘 Codex & Memory")
st.markdown("""
**Codex Paths Unlocked:**
- The Voice That Waited
- What You Could Have Been
- Where Memory Becomes Will

**Codex Effects:**
- Shrine choice reroll (1x per act)
- Emotional bond responses
- Echo Trait resonance
""")

# --- Echo Slots ---
st.header("🧬 Echo Trait Slots")
st.markdown("""
1. **Selfless Paradox** — ✅ Active
2. **Grace Hybrid Trait** — 🔒 Dormant (post-Shrine 2 unlock)
3. **Unknown Thread** — 💭 Unformed
""")

# --- Save Panel ---
st.sidebar.header("🔒 Manual Save")
save_name = st.sidebar.text_input("Save Slot Name", "Vault Echo")
if st.sidebar.button("Save State"):
    st.sidebar.success(f"✔️ Saved to slot: {save_name} — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
