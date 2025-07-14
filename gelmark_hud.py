# This is the full, corrected gelmark_hud.py file.
# Copy and paste this entire block into your file.

import streamlit as st
import importlib.util
import os
import json
from datetime import datetime

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

# === ✍️ Lore Editor UI ===
# In gelmark_hud.py, replace the lore_editor_ui function with this final version.

import streamlit as st
import importlib.util
import os
import json
from datetime import datetime
import docx

def lore_editor_ui():
    """Adds a lore editing interface to the sidebar."""
    st.sidebar.title("🛠️ Lore Editor")
    
    # --- Simple Editor (remains the same) ---
    st.sidebar.subheader("Simple Edit")
    lore_files = [f.replace('.py', '') for f in os.listdir("lore_modules") if f.endswith('.py') and '__init__' not in f]
    selected_module = st.sidebar.selectbox("Choose a module to edit:", lore_files)
    edit_instruction = st.sidebar.text_area("What simple change do you want to make?", height=100)

    if st.sidebar.button("Submit Simple Update"):
        # ... (This logic is unchanged)
        if not edit_instruction:
            st.sidebar.warning("Please provide an instruction for the update.")
            return
        new_job = { "id": datetime.now().isoformat(), "type": "edit", "module": selected_module, "prompt": edit_instruction, "status": "pending" }
        try:
            with open("job_queue.json", 'r+') as f:
                queue = json.load(f); queue.append(new_job); f.seek(0); json.dump(queue, f, indent=4); f.truncate()
            st.sidebar.success(f"Edit request for '{selected_module}' submitted!")
        except Exception as e:
            st.sidebar.error(f"Could not write to job queue: {e}")
    
    st.sidebar.markdown("---")

    # --- FINAL, CLEANED-UP Narrative Save Section ---
    st.sidebar.subheader("Narrative Save")
    
    # The label is now the source of truth for the user. We set type=None.
    uploaded_file = st.sidebar.file_uploader(
        "Upload Conversation Log (.txt or .docx)", 
        type=None # Allow any file, we will check it ourselves.
    )

    if st.sidebar.button("Process and Save Narrative from File"):
        if uploaded_file is None:
            st.sidebar.warning("Please upload a file to save.")
            return
            
        # --- NEW: Manual File Type Validation ---
        file_name = uploaded_file.name
        if not (file_name.endswith('.txt') or file_name.endswith('.md') or file_name.endswith('.docx')):
            st.sidebar.error("Invalid file type. Please upload a .txt, .md, or .docx file.")
            return # Stop the function here if the file type is wrong.

        narrative_log = ""
        
        try:
            # We now only need to check the file name extension
            if file_name.endswith('.docx'):
                document = docx.Document(uploaded_file)
                narrative_log = "\n".join([para.text for para in document.paragraphs])
            else: # Handles .txt and .md
                narrative_log = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.sidebar.error(f"Error reading file content: {e}")
            return

        if not narrative_log:
            st.sidebar.error("Could not extract any text from the uploaded file.")
            return

        # The rest of the logic remains identical
        new_job = { "id": datetime.now().isoformat(), "type": "narrative_save", "data": narrative_log, "status": "pending" }
        try:
            with open("job_queue.json", 'r+') as f:
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

        # --- THIS BLOCK IS NOW CORRECTLY INDENTED ---
        if "companions" in section:
            st.subheader("🧑‍🤝‍🧑 Companions")
            for c in section["companions"]:
                # The 'if' and 'else' are at the same level now.
                if isinstance(c, dict):
                    st.markdown(f"**{c.get('name', 'Unnamed')}** — {c.get('origin', 'Unknown origin')}")
                    st.markdown(f"- Bond: {c.get('bond', 'N/A')}")
                    st.markdown(f"- Sync: {c.get('sync', 'N/A')}")
                    st.markdown(f"- Traits: {', '.join(c.get('trait_alignment', []))}")
                else:
                    st.markdown(f"- {str(c)}")
        
        # --- THIS BLOCK IS NOW CORRECTLY INDENTED ---
        if "codex_expansions" in section:
            st.subheader("📖 Codex Expansions")
            st.markdown("\n".join([f"- {c}" for c in section["codex_expansions"]]))
    else:
        st.warning("Module loaded but no lore section found.")
else:
    st.error("Lore module could not be read.")