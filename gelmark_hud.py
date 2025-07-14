import streamlit as st
import importlib.util
import os

# === 📁 Modular Lore Loader ===

def load_lore_module(module_name):
    try:
        path = os.path.join("lore_modules", f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name, path)
        lore_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lore_module)
        return lore_module
    except Exception as e:
        st.error(f"Failed to load module: {module_name} - {e}")
        return None

# === 📊 Gelmark Lore HUD ===
st.set_page_config(page_title="Gelmark Lore HUD", layout="wide")
st.title("📖 Gelmark Interactive Lore HUD")

pages = {
    "Prologue": "prologue",
    "Act 1": "act1",
    "Act 2": "act2"
}

selected_page = st.sidebar.radio("Lore Sections", list(pages.keys()))

module_key = pages[selected_page]
lore_data = load_lore_module(module_key)

if lore_data:
    section = getattr(lore_data, f"{module_key}_lore", None)

    if section:
        st.subheader(f"📘 {selected_page} Summary")
        st.markdown(section.get("summary", "No summary provided."))

        if "key_events" in section:
            st.subheader("🧩 Key Events")
            st.markdown("\n".join([f"- {event}" for event in section["key_events"]]))

        if "shrines" in section:
            st.subheader("🛕 Shrines")
            for shrine in section["shrines"]:
                st.markdown(f"**Shrine {shrine['id']}: {shrine['name']}**")
                st.markdown(f"- Unlocks: {', '.join(shrine['unlocks'])}")
                st.markdown(f"- Traits: {', '.join(shrine['traits'])}")

        if "visions" in section:
            st.subheader("🔮 Visions")
            st.markdown("\n".join([f"- {v}" for v in section["visions"]]))

        if "companions" in section:
            st.subheader("🧍 Companions")
            for c in section["companions"]:
                    if isinstance(c, dict):
                    st.markdown(f"**{c.get('name', 'Unnamed')}** — {c.get('origin', 'Unknown origin')}")
            else:
                    st.markdown(str(c))
                    st.markdown(f"- Bond: {c['bond']}")
                    st.markdown(f"- Sync: {c['sync']}")
                    st.markdown(f"- Traits: {', '.join(c['trait_alignment'])}")

        if "codex_expansions" in section:
            st.subheader("📖 Codex Expansions")
            st.markdown("\n".join([f"- {c}" for c in section["codex_expansions"]]))
    else:
        st.warning("Module loaded but no lore section found.")
else:
    st.error("Lore module could not be read.")
