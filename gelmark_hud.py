# This is the final, corrected gelmark_hud.py file.
# It now intelligently handles different formats in the 'companions' list.

import streamlit as st
import importlib.util
import os
import json
from datetime import datetime
import docx

# === 📁 Modular Lore Loader ===
def load_lore_module(module_name):
    try:
        path = os.path.join("my_gm", "lore_modules", f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name, path)
        lore_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lore_module)
        return lore_module
    except Exception as e:
        st.error(f"Failed to load module: {module_name} - {e}")
        return None

# === ✍️ Lore Editor UI ===
def lore_editor_ui():
    st.sidebar.title("🛠️ Lore Editor")
    LORE_DIR = os.path.join("my_gm", "lore_modules")
    JOB_QUEUE_PATH = os.path.join("my_gm", "job_queue.json")

    if not os.path.exists(LORE_DIR):
        st.sidebar.error(f"FATAL ERROR: Directory '{LORE_DIR}' not found.")
        return

    st.sidebar.subheader("Narrative Save")
    uploaded_file = st.sidebar.file_uploader("Upload Conversation Log", type=['txt', 'md', 'docx'])

    if st.sidebar.button("Process and Save Narrative from File"):
        if uploaded_file is None: st.sidebar.warning("Please upload a file."); return
        narrative_log = ""
        try:
            if uploaded_file.name.endswith('.docx'):
                document = docx.Document(uploaded_file)
                narrative_log = "\n".join([para.text for para in document.paragraphs])
            else:
                narrative_log = uploaded_file.read().decode("utf-8")
        except Exception as e: st.sidebar.error(f"Error reading file: {e}"); return
        if not narrative_log: st.sidebar.error("Could not extract text."); return
        new_job = { "id": datetime.now().isoformat(), "type": "narrative_save", "data": narrative_log, "status": "pending" }
        try:
            if not os.path.exists(JOB_QUEUE_PATH): queue = []
            else:
                with open(JOB_QUEUE_PATH, 'r') as f: queue = json.load(f)
            queue.append(new_job)
            with open(JOB_QUEUE_PATH, 'w') as f: json.dump(queue, f, indent=4)
            st.sidebar.success("Narrative save request submitted!"); st.balloons()
        except Exception as e: st.sidebar.error(f"Could not write to job queue: {e}")

# === 📊 Gelmark Lore HUD ===
st.set_page_config(page_title="Gelmark Lore HUD", layout="wide")
st.title("📖 Gelmark Interactive Lore HUD")

pages = { "Prologue": "prologue", "Act 1": "act1", "Act 2": "act2" }
selected_page = st.sidebar.radio("Lore Sections", list(pages.keys()))
lore_editor_ui()
st.sidebar.markdown("---")
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
                st.markdown(f"**Shrine {shrine.get('id', 'N/A')}: {shrine.get('name', 'Unnamed')}**")
                st.markdown(f"- Unlocks: {', '.join(shrine.get('unlocks', []))}")
                st.markdown(f"- Traits: {', '.join(shrine.get('traits', []))}")

        if "visions" in section:
            st.subheader("🔮 Visions")
            st.markdown("\n".join([f"- {v}" for v in section["visions"]]))
            
        # --- THIS BLOCK IS NOW FIXED ---
        if "companions" in section:
            st.subheader("🧑‍🤝‍🧑 Companions")
            for c in section["companions"]:
                # Check if 'c' is a dictionary with details
                if isinstance(c, dict):
                    st.markdown(f"**{c.get('name', 'Unnamed')}** — {c.get('origin', 'Unknown origin')}")
                    st.markdown(f"- Bond: {c.get('bond', 'N/A')}")
                    st.markdown(f"- Sync: {c.get('sync', 'N/A')}")
                    st.markdown(f"- Traits: {', '.join(c.get('trait_alignment', []))}")
                # Otherwise, just print it as a simple string
                else:
                    st.markdown(f"- {str(c)}")
        # --- END OF FIX ---
        
        if "codex_expansions" in section:
            st.subheader("📖 Codex Expansions")
            st.markdown("\n".join([f"- {c}" for c in section["codex_expansions"]]))

    else:
        st.warning(f"Variable '{module_key}_lore' not found in the lore module.")
else:
    st.error("Lore module could not be read. Check file paths and content.")