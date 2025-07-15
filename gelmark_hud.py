# This is the full and correct gelmark_hud.py file.
# It includes all the display logic for every section of the lore.

import streamlit as st
import importlib.util
import os
import json
from datetime import datetime
import docx

# === 📁 Modular Lore Loader (Corrected Path) ===
def load_lore_module(module_name):
    try:
        # Path now correctly points to 'my_gm'
        path = os.path.join("my_gm", "lore_modules", f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name, path)
        lore_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lore_module)
        return lore_module
    except Exception as e:
        st.error(f"Failed to load module: {module_name} - {e}")
        return None

# === ✍️ Lore Editor UI (Corrected Paths) ===
def lore_editor_ui():
    """Adds a lore editing interface to the sidebar."""
    st.sidebar.title("🛠️ Lore Editor")
    
    # Define paths to the correct folder
    LORE_DIR = os.path.join("my_gm", "lore_modules")
    JOB_QUEUE_PATH = os.path.join("my_gm", "job_queue.json")

    if not os.path.exists(LORE_DIR):
        st.sidebar.error(f"FATAL ERROR: The directory '{LORE_DIR}' was not found.")
        return

    # --- Simple Editor ---
    st.sidebar.subheader("Simple Edit")
    lore_files = [f.replace('.py', '') for f in os.listdir(LORE_DIR) if f.endswith('.py') and '__init__' not in f]
    selected_module = st.sidebar.selectbox("Choose a module to edit:", lore_files)
    edit_instruction = st.sidebar.text_area("What simple change do you want to make?", height=100)

    if st.sidebar.button("Submit Simple Update"):
        if not edit_instruction: st.sidebar.warning("Please provide an instruction."); return
        new_job = { "id": datetime.now().isoformat(), "type": "edit", "module": selected_module, "prompt": edit_instruction, "status": "pending" }
        try:
            if not os.path.exists(JOB_QUEUE_PATH): queue = []
            else:
                with open(JOB_QUEUE_PATH, 'r') as f: queue = json.load(f)
            queue.append(new_job)
            with open(JOB_QUEUE_PATH, 'w') as f: json.dump(queue, f, indent=4)
            st.sidebar.success(f"Edit request for '{selected_module}' submitted!")
        except Exception as e: st.sidebar.error(f"Could not write to job queue: {e}")
    
    st.sidebar.markdown("---")
    
    # --- Narrative Save Section ---
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
        except Exception as e: st.sidebar.error(f"Error reading file content: {e}"); return
        if not narrative_log: st.sidebar.error("Could not extract any text."); return
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

# --- Sidebar Navigation ---
pages = { "Prologue": "prologue", "Act 1": "act1", "Act 2": "act2" }
selected_page = st.sidebar.radio("Lore Sections", list(pages.keys()))

# --- Render the Editor UI ---
lore_editor_ui()

# --- Main Page Display Logic (Now Complete) ---
module_key = pages[selected_page]
lore_data = load_lore_module(module_key)

if lore_data:
    section = getattr(lore_data, f"{module_key}_lore", None)
    if section:
        st.subheader(f"📘 {selected_page} Summary")
        st.markdown(section.get("summary", "No summary provided."))

        # --- THIS IS THE LOGIC THAT WAS MISSING ---
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
            st.subheader("🧑‍🤝‍🧑 Companions")
            for c in section["companions"]:
                st.markdown(f"**{c.get('name', 'Unnamed')}** — {c.get('origin', 'Unknown origin')}")
                st.markdown(f"- Bond: {c.get('bond', 'N/A')}")
                st.markdown(f"- Sync: {c.get('sync', 'N/A')}")
                st.markdown(f"- Traits: {', '.join(c.get('trait_alignment', []))}")
        
        if "codex_expansions" in section:
            st.subheader("📖 Codex Expansions")
            st.markdown("\n".join([f"- {c}" for c in section["codex_expansions"]]))
        # --- END OF MISSING LOGIC ---

    else:
        st.warning(f"Variable '{module_key}_lore' not found in the lore module.")
else:
    st.error("Lore module could not be read. Check file paths and content.")