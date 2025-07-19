# This is the final, feature-complete version of the local application.
# It is designed to display the full, standardized lore page structure.

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
    """Loads a Python file from the lore_modules directory."""
    try:
        path = os.path.join(LORE_FOLDER, f"{module_name}.py")
        if not os.path.exists(path): return None
        # Use a unique name for the module based on its path to avoid cache issues
        module_name_unique = f"lore_{module_name}"
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
    """The main AI logic function."""
    st.info("Preparing lore and contacting the Gemini AI...")
    current_lore = get_all_lore_content()
    lore_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in current_lore.items()])

    # The prompt now includes instructions for the new detailed structure
    prompt = f"""You are a master storyteller and game lore keeper. Your task is to update the game's lore files based on a new narrative log, following a very specific structure.
NARRATIVE LOG: <log>{narrative_log}</log>
CURRENT LORE FILES: <lore>{lore_string}</lore>
INSTRUCTIONS:
1. Analyze the log and the current lore.
2. Update the Python dictionaries in the lore files to reflect the new information. Populate all relevant fields: summary, major_events, companions_bond_status, traits_unlocked, etc.
3. Your response MUST be a single, valid JSON object. Keys must be the FILENAMES (e.g., "act1.py") and values must be the COMPLETE, new file content as a single Python code string.
4. Ensure all lists, dictionaries, and strings in the Python code are syntactically correct.
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

# --- UI Functions ---

def display_section(title, data):
    """Generic function to display a section if data exists."""
    if data:
        st.subheader(title)
        if isinstance(data, list):
            for item in data:
                # If item is a dictionary, display it nicely
                if isinstance(item, dict):
                    # Create a title from 'name' or 'id' if available
                    item_title = item.get('name', item.get('id', 'Entry'))
                    with st.container():
                         st.markdown(f"**{item_title}**")
                         for k, v in item.items():
                             # Don't repeat the title key
                             if k.lower() not in ['name', 'id']:
                                 st.markdown(f"- **{k.replace('_', ' ').title()}:** {v}")
                # Otherwise, it's a simple list item
                else:
                    st.markdown(f"- {item}")
        # If it's not a list, just write it
        else:
            st.markdown(data)

# --- Main App Interface ---
st.title("📖 Gelmark Local Lore Editor")
st.sidebar.title("🛠️ Lore Updater")
st.sidebar.subheader("Paste Narrative Log")
narrative_log_input = st.sidebar.text_area("Paste your new story information here:", height=300)

if st.sidebar.button("Process and Update Lore"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("GEMINI_API_KEY is not set!")
    elif not narrative_log_input:
        st.sidebar.warning("Please paste a narrative log.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("The AI is rewriting the lore..."):
            success = run_lore_update(narrative_log_input)
        
        if success:
            st.success("Lore files updated successfully! Refresh the page (F5) to see the new content.")
            st.balloons()
        else:
            st.error("The lore update failed. See details above.")

# --- Main Display Area ---
st.sidebar.markdown("---")
pages = {"Prologue": "prologue", "Act 1": "act1", "Act 2": "act2"}
selected_page = st.sidebar.radio("View Lore Section:", list(pages.keys()))
module_data = load_lore_module(pages[selected_page])

if module_data:
    section_variable_name = f"{pages[selected_page]}_lore"
    section_data = getattr(module_data, section_variable_name, {})

    if not section_data:
        st.warning(f"Could not find the lore dictionary named `{section_variable_name}` in `{pages[selected_page]}.py`.")
    else:
        # Use our generic display function for each section
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
    st.error(f"Could not read the lore module for '{selected_page}'.")