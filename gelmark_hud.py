This is another excellent step forward! The error has changed again, which means we are successfully fixing issues one by one.

This FileNotFoundError is the direct result of the changes we made to fix the GitHub Actions bot. It's the other side of the same coin.

The Problem

Your GitHub bot needed the lore_modules folder to be inside the My gm folder.

Your Streamlit web app (gelmark_hud.py) is still running in the main (root) directory, and it's looking for lore_modules right next to it.

The app can't find the folder because we moved it.

The error message confirms this: os.listdir("lore_modules") failed because there is no folder named lore_modules in the root directory anymore.

The Solution: Update Paths in gelmark_hud.py

We need to tell your Streamlit app to look inside the My gm folder to find the files it needs. This involves changing two functions in gelmark_hud.py.

Here is the complete, corrected code for your gelmark_hud.py file. You can simply replace the entire file with this block.

Generated python
# This is the full, corrected gelmark_hud.py file.
# It now looks for lore files inside the "My gm" directory.

import streamlit as st
import importlib.util
import os
import json
from datetime import datetime
import docx

# === 📁 Modular Lore Loader (Corrected Path) ===
def load_lore_module(module_name):
    try:
        # UPDATED: Path now includes "My gm"
        path = os.path.join("My gm", "lore_modules", f"{module_name}.py")
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
    
    # --- Simple Editor ---
    st.sidebar.subheader("Simple Edit")

    # UPDATED: Path now includes "My gm"
    LORE_DIR = os.path.join("My gm", "lore_modules")
    JOB_QUEUE_PATH = os.path.join("My gm", "job_queue.json")

    lore_files = [f.replace('.py', '') for f in os.listdir(LORE_DIR) if f.endswith('.py') and '__init__' not in f]
    selected_module = st.sidebar.selectbox("Choose a module to edit:", lore_files)
    edit_instruction = st.sidebar.text_area("What simple change do you want to make?", height=100)

    if st.sidebar.button("Submit Simple Update"):
        if not edit_instruction:
            st.sidebar.warning("Please provide an instruction for the update.")
            return
        new_job = { "id": datetime.now().isoformat(), "type": "edit", "module": selected_module, "prompt": edit_instruction, "status": "pending" }
        try:
            # UPDATED: Path to job_queue.json is now correct
            with open(JOB_QUEUE_PATH, 'r+') as f:
                queue = json.load(f); queue.append(new_job); f.seek(0); json.dump(queue, f, indent=4); f.truncate()
            st.sidebar.success(f"Edit request for '{selected_module}' submitted!")
        except Exception as e:
            st.sidebar.error(f"Could not write to job queue: {e}")
    
    st.sidebar.markdown("---")

    # --- Narrative Save Section ---
    st.sidebar.subheader("Narrative Save")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload Conversation Log (.txt or .docx)", 
        type=['txt', 'md', 'docx']
    )

    if st.sidebar.button("Process and Save Narrative from File"):
        if uploaded_file is None:
            st.sidebar.warning("Please upload a file to save.")
            return

        narrative_log = ""
        file_name = uploaded_file.name
        
        try:
            if file_name.endswith('.docx'):
                document = docx.Document(uploaded_file)
                narrative_log = "\n".join([para.text for para in document.paragraphs])
            else:
                narrative_log = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.sidebar.error(f"Error reading file content: {e}")
            return

        if not narrative_log:
            st.sidebar.error("Could not extract any text from the uploaded file.")
            return

        new_job = { "id": datetime.now().isoformat(), "type": "narrative_save", "data": narrative_log, "status": "pending" }
        try:
            # UPDATED: Path to job_queue.json is now correct
            with open(JOB_QUEUE_PATH, 'r+') as f:
                queue = json.load(f); queue.append(new_job); f.seek(0); json.dump(queue, f, indent=4); f.truncate()
            st.sidebar.success("Narrative save request from file submitted!")
            st.balloons()
        except Exception as e:
            st.sidebar.error(f"Could not write to job queue: {e}")

# === 📊 Gelmark Lore HUD ===
st.set_page_config(page_title="Gelmark Lore HUD", layout="wide")
st.title("📖 Gelmark Interactive Lore HUD")

# --- Sidebar Navigation ---
pages = { "Prologue": "prologue", "Act 1": "act1", "Act 2": "act2" }
selected_page = st.sidebar.radio("Lore Sections", list(pages.keys()))

# --- Lore Editor ---
lore_editor_ui()
st.sidebar.markdown("---")

# --- Main Page Display Logic ---
module_key = pages[selected_page]
lore_data = load_lore_module(module_key)

if lore_data:
    section = getattr(lore_data, f"{module_key}_lore", None)
    if section:
        # ... (rest of the display logic is unchanged and correct) ...
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
            st.subheader("🧑‍🤝‍🧑 Companions")
            for c in section["companions"]:
                if isinstance(c, dict):
                    st.markdown(f"**{c.get('name', 'Unnamed')}** — {c.get('origin', 'Unknown origin')}")
                    st.markdown(f"- Bond: {c.get('bond', 'N/A')}")
                    st.markdown(f"- Sync: {c.get('sync', 'N/A')}")
                    st.markdown(f"- Traits: {', '.join(c.get('trait_alignment', []))}")
                else:
                    st.markdown(f"- {str(c)}")
        
        if "codex_expansions" in section:
            st.subheader("📖 Codex Expansions")
            st.markdown("\n".join([f"- {c}" for c in section["codex_expansions"]]))
    else:
        st.warning("Module loaded but no lore section found.")
else:
    st.error("Lore module could not be read.")

Summary of Changes:

In load_lore_module(), the path to the lore files was changed to: os.path.join("My gm", "lore_modules", ...)

In lore_editor_ui(), the paths for both lore_modules and job_queue.json were updated to point inside the My gm directory.

Once you commit this updated gelmark_hud.py file, your Streamlit app should load correctly.