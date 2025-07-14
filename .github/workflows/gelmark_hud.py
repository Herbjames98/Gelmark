import streamlit as st
import importlib.util
import os
import json
from datetime import datetime

# === 📁 Modular Lore Loader ===
# (Your existing load_lore_module function remains unchanged)
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

# === ✍️ New Function: Lore Editor UI ===
def lore_editor_ui():
    """Adds a lore editing interface to the sidebar."""
    st.sidebar.title("🛠️ Lore Editor")
    
    # Get a list of lore files to choose from
    lore_files = [f.replace('.py', '') for f in os.listdir("lore_modules") if f.endswith('.py')]
    
    selected_module = st.sidebar.selectbox("Choose a module to edit:", lore_files)
    edit_instruction = st.sidebar.text_area("What change do you want to make?", height=100)

    if st.sidebar.button("Submit Update Request"):
        if not edit_instruction:
            st.sidebar.warning("Please provide an instruction for the update.")
            return

        # Create a new job dictionary
        new_job = {
            "id": datetime.now().isoformat(), # Unique ID for the job
            "module": selected_module,
            "prompt": edit_instruction,
            "status": "pending"
        }

        # Add the job to our queue file
        try:
            with open("job_queue.json", 'r+') as f:
                queue = json.load(f)
                queue.append(new_job)
                f.seek(0) # Rewind to the start of the file
                json.dump(queue, f, indent=4)
                f.truncate() # Remove any old data if the new file is smaller
            st.sidebar.success(f"Request submitted! The lore for '{selected_module}' will be updated shortly.")
        except Exception as e:
            st.sidebar.error(f"Could not write to job queue: {e}")

# === 📊 Gelmark Lore HUD ===
st.set_page_config(page_title="Gelmark Lore HUD", layout="wide")
st.title("📖 Gelmark Interactive Lore HUD")

# --- Sidebar Navigation ---
pages = { "Prologue": "prologue", "Act 1": "act1", "Act 2": "act2" }
selected_page = st.sidebar.radio("Lore Sections", list(pages.keys()))

# --- NEW: Add the Lore Editor to the sidebar ---
lore_editor_ui()
st.sidebar.markdown("---") # Visual separator

# --- Main Page Display Logic ---
# (Your existing display logic remains unchanged)
module_key = pages[selected_page]
lore_data = load_lore_module(module_key)

if lore_data:
    section = getattr(lore_data, f"{module_key}_lore", None)
    if section:
        st.subheader(f"📘 {selected_page} Summary")
        st.markdown(section.get("summary", "No summary provided."))
        # ... (rest of your display logic for key events, shrines, etc.)
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
        # This 'if' statement is the key fix.
        # It checks if 'c' is a dictionary before trying to access its keys.
                if isinstance(c, dict):
                    st.markdown(f"**{c.get('name', 'Unnamed')}** — {c.get('origin', 'Unknown origin')}")
                    st.markdown(f"- Bond: {c.get('bond', 'N/A')}")
                    st.markdown(f"- Sync: {c.get('sync', 'N/A')}")
                    st.markdown(f"- Traits: {', '.join(c.get('trait_alignment', []))}")
        else:
            # If 'c' is not a dictionary (e.g., just a string), print it directly.
            st.markdown(f"- {str(c)}")
        if "codex_expansions" in section:
            st.subheader("📖 Codex Expansions")
            st.markdown("\n".join([f"- {c}" for c in section["codex_expansions"]]))
    else:
        st.warning("Module loaded but no lore section found.")
else:
    st.error("Lore module could not be read.")