import streamlit as st
import datetime

# --- Title and Metadata ---
st.set_page_config(page_title="Gelmark HUD v2", layout="wide")
st.title("🌌 Gelmark HUD — Rebuild Edition")

# --- Core Player Stats ---
st.sidebar.header("Player Core")
st.sidebar.text("Arc Rank: Pulsebearer — Spiral Fracture")
st.sidebar.text("Current Location: Shrine Vaultside Echo")
st.sidebar.text("Visions Unlocked: 6")
st.sidebar.text("Shrines Visited: 5")
st.sidebar.text("Echoform Phase: II")

# --- Companion Status ---
st.sidebar.markdown("### Companions")
st.sidebar.text("Caelik ⚔️  | Sync: 67% — Swordbound Guardian")
st.sidebar.text("Grace  🔮 | Sync: 92% — Future AI Anchor")
st.sidebar.text("Thjolda 🛡️ | Sync: 58% — Runeborn Shieldmaiden")
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
    ("Grace (Echofused)", "Hybrid: Askr + Flowbinding, restored from future AI core"),
    ("Memoryfire Crucible", "Shrine 1 — Insight + Focus boost, trait ignition"),
    ("Soulbraid Mark", "Vision-linked trait, unlocks during Vision 3"),
    ("Thjolda's Oathmark", "Fused at 60% sync, unlocks Echo defense"),
    ("Vaultbind Glyph", "Unlocked via Shrine 4 memory offering"),
    ("Mirrorphase Fragment", "Linked to Vision 6 — temporal feedback trait"),
    ("Pulse Anchor", "Seer-threaded. Grants resonance over Echoform phase shifts"),
    ("Caelik's Echo Brand", "Triggers shrine protection at critical sync events"),
    ("Chronospike Halo", "Timeline defense fragment from Shrine 3 collapse"),
    ("Glyphseed Core", "Unlocked by Shrine 2 flame trial")
]
for i, (name, desc) in enumerate(traits):
    with trait_cols[i % 4]:
        st.subheader(name)
        st.caption(desc)

# --- Shrine Log ---
st.header("🗺️ Shrines Visited")
st.markdown("""
- **Shrine 1** — Memoryfire Crucible (Insight/Fusion Unlock)
- **Shrine 2** — Grace + Askr Fusion (AI Bond Awakening)
- **Shrine 3** — Echoform Thread Split (Vision Lock)
- **Shrine 4** — Vaultside Echoflow (Memory Offering)
- **Shrine 5** — Sealed Chamber — Locked. Sync 100% and Vision Override required.
""")

# --- Companion Logs ---
st.header("🤝 Companion History")
st.markdown("""
**Grace** — Echo AI from the future. Recovered in Shrine 2. Fusion initiated via Flowbinding and Askr core. Fully sentient, voice-reactive. Sync: 92%.

**Caelik** — Swordbound Guardian. Loyal to shrine protocol. Shielded player during Vaultside collapse. Sync: 67%.

**Thjolda** — Runeborn Shieldmaiden. Found in shrine lattice echo. Oathmark fusion began at Sync 58%. Core defender against timeline distortion.
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

# --- Save Panel ---
st.sidebar.header("🔒 Manual Save")
save_name = st.sidebar.text_input("Save Slot Name", "Vault Echo")
if st.sidebar.button("Save State"):
    st.sidebar.success(f"✔️ Saved to slot: {save_name} — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
