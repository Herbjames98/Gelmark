# This is the final, feature-complete version of the local application.
# The AI prompt has been upgraded to ensure it populates the correct lore file.

import streamlit as st
import os
import json
import google.generativeai as genai
import docx
import importlib.util

# --- Configuration and Setup ---
st.set_page_config(page_title="Gelmark Lore HUD", layout="wide")
LORE_FOLDER = os.path.join("my_gm", "lore_modules")

# --- Core Functions ---

def load_lore_module(module_name):
    """Loads a Python file from the lore_modules directory, avoiding cache issues."""
    try:
        path = os.path.join(LORE_FOLDER, f"{module_name}.py")
        if not os.path.exists(path): return None
        module_name_unique = f"lore_module_{module_name}_{os.path.getmtime(path)}"
        spec = importlib.util.spec_from_file_location(module_name_unique, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        st.error(f"Error loading {module_name}: {e}")
        return None

def get_all_lore_content():
    """Reads all current lore files into a dictionary."""
    all_lore = {}
    for filename in os.listdir(LORE_FOLDER):
        if filename.endswith('.py') and '__init__' not in filename:
            filepath = os.path.join(LORE_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                all_lore[filename] = f.read()
    return all_lore

def run_lore_update(narrative_log):
    """The main AI logic function with upgraded, more precise instructions."""
    st.info("Preparing lore and contacting the Gemini AI...")
    current_lore = get_all_lore_content()
    lore_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in current_lore.items()])

    # --- THIS PROMPT IS NOW SMARTER ---
    prompt = f"""You are a master storyteller and game lore keeper for a dark fantasy world named Gelmark. Your task is to update the game's lore files based on a new narrative log.
NARRATIVE LOG: <log>{narrative_log}</log>
CURRENT LORE FILES: <lore>{lore_string}</lore>
INSTRUCTIONS:
1.  First, analyze the narrative log to determine which act it belongs to (e.g., Prologue, Act 1, Act 2, etc.).
2.  CRITICAL: Select ONLY the corresponding lore file (e.g., `prologue.py`, `act1.py`) that matches the narrative's context. Do NOT add Act 2 events to the Act 1 file.
3.  Populate all 16 sections of the chosen file with a high level of detail based on the log.
4.  Your response MUST be a single, valid JSON object. The keys must be the filename(s) you have modified, and the values must be the COMPLETE, new Python code content for that file.
5.  Only return the file(s) you have actually changed.
Return ONLY the raw JSON object."""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        updated_files = json.loads(response.text.strip().removeprefix("```json").removesuffix("```"))
    except Exception as e:
        st.error(f"An error occurred while processing the AI response: {e}")
        st.subheader("Raw AI Response:")
        st.code(response.text if 'response' in locals() else "No response from AI.", language="text")
        return False

    if not updated_files:
        st.warning("The AI returned an empty response. No files were changed.")
        return False
        
    st.info("AI processing complete. Writing changes to local files...")
    for key, content in updated_files.items():
        filename = os.path.basename(key) 
        if filename in current_lore:
            filepath = os.path.join(LORE_FOLDER, filename)
            with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
    return True

# --- UI Display Functions ---
def display_section(title, data):
    if data:
        st.subheader(title)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item_title = item.get('name', item.get('term', item.get('id', 'Entry')))
                    with st.container():
                         st.markdown(f"**{item_title}**")
                         for k, v in item.items():
                             if k.lower() not in ['name', 'term', 'id']:
                                 st.markdown(f"- **{k.replace('_', ' ').title()}:** {v}")
                else:
                    st.markdown(f"- {item}")
        else:
            st.markdown(data)

# --- Main App Interface ---
st.title("📖 Gelmark Local Lore Editor")
st.sidebar.title("🛠️ Lore Updater")
st.sidebar.subheader("Paste Narrative Log")
narrative_log_input = st.sidebar.text_area("Paste your new story information here:", height=300)

if st.sidebar.button("Process and Update Lore"):
    if not os.getenv("GEMINI_API_KEY"): st.sidebar.error("GEMINI_API_KEY is not set!")
    elif not narrative_log_input: st.sidebar.warning("Please paste a narrative log.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("The AI is rewriting the lore..."):
            success = run_lore_update(narrative_log_input)
        
        if success:
            st.success("Lore files updated successfully! The page will now reload.")
            st.balloons()
            st.rerun()
        else:
            st.error("The lore update failed. See details above.")

# --- Main Display Area ---
st.sidebar.markdown("---")
# This will now automatically find any .py file in the lore folder
lore_files = sorted([f.replace('.py', '') for f in os.listdir(LORE_FOLDER) if f.endswith('.py') and '__init__' not in f])
pages = {file.replace('_', ' ').title(): file for file in lore_files}

if pages:
    selected_page_title = st.sidebar.radio("View Lore Section:", list(pages.keys()))
    selected_module_name = pages[selected_page_title]
    module_data = load_lore_module(selected_module_name)

    if module_data:
        section_variable_name = f"{selected_module_name}_lore"
        section_data = getattr(module_data, section_variable_name, {})
        if not section_data:
            st.warning(f"Could not find the lore dictionary named `{section_variable_name}` in `{selected_module_name}.py`.")
        else:
            display_section("📘 Summary", section_data.get("summary"))
            display_section("🧩 Major Events", section_data.get("major_events"))
            display_section("🧑‍🤝‍🧑 Companions & Bond Status", section_data.get("companions_bond_status"))
            display_section("✨ Traits Unlocked", section_data.get("traits_unlocked"))
            display_section("🛕 Shrines Visited", section_data.get("shrines_visited"))
            display_section("🔮 Visions & Echo Sequences", section_data.get("visions_echo_sequences"))
            display_section("📖 Lore Entries / Codex Expansions", section_data.get("lore_codex_expansions"))
            display_section("⏳ Timeline Edits", section_data.get("timeline_edits"))
            display_section("🔑 Key Terms Introduced", section_data.get("key_terms_introduced"))
            display_section("🗺️ Locations & Realms Visited", section_data.get("locations_realms_visited"))
            display_section("👽 Faction or Threat Encounters", section_data.get("faction_threat_encounters"))
            display_section("📜 Oaths & Rituals Performed", section_data.get("oaths_rituals_performed"))
            display_section("🏺 Artifacts Discovered", section_data.get("artifacts_discovered"))
            display_section("❓ Narrative Threads Opened", section_data.get("narrative_threads_opened"))
            display_section("✅ Narrative Threads Closed", section_data.get("narrative_threads_closed"))
    else:
        st.error(f"Could not read the lore module for '{selected_page_title}'.")
else:
    st.warning(f"No lore files found in the '{LORE_FOLDER}' directory.")
```Your workflow is now perfectly set up. You can create new, empty act files with the template, and the AI will be much more intelligent about placing the right story beats in the right file.