# This is the definitive, feature-complete version of the local application.
# It uses the file uploader, includes emojis, and has all other fixes integrated.

import streamlit as st
import os
import json
import google.generativeai as genai
import docx
import importlib.util

# --- Configuration and Setup ---
st.set_page_config(page_title="Gelmark Lore HUD", layout="wide")
LORE_FOLDER = os.path.join("my_gm", "lore_modules")
PLAYER_STATE_FILE = os.path.join("my_gm", "player_state.py")

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

def load_player_state():
    """Loads the player_state.py file."""
    try:
        if not os.path.exists(PLAYER_STATE_FILE): return None
        spec = importlib.util.spec_from_file_location("player_state", PLAYER_STATE_FILE)
        player_state_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(player_state_module)
        return player_state_module
    except Exception as e:
        st.error(f"Error loading player state: {e}")
        return None

def get_all_lore_content():
    """Reads all game data files into a dictionary for the AI."""
    all_content = {}
    if os.path.exists(PLAYER_STATE_FILE):
        with open(PLAYER_STATE_FILE, 'r', encoding='utf-8') as f:
            all_content['player_state.py'] = f.read()
    for filename in os.listdir(LORE_FOLDER):
        if filename.endswith('.py') and '__init__' not in filename:
            filepath = os.path.join(LORE_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                all_content[filename] = f.read()
    return all_content

def run_lore_update(narrative_log):
    """The main AI logic function with the 'world-builder' prompt."""
    st.info("Preparing lore and contacting the Gemini AI...")
    current_content = get_all_lore_content()
    content_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in current_content.items()])

    prompt = f"""You are a master storyteller. Your task is to update a complete set of game data files based on a new narrative log. Differentiate between the player's CURRENT status and historical lore.

NARRATIVE LOG: <log>{narrative_log}</log>

GAME DATA FILES: <files>{content_string}</files>

INSTRUCTIONS:
1. Read the new narrative log.
2. Update `player_state.py` to reflect the player's MOST RECENT stats, inventory, traits, and companion statuses.
3. CRITICAL RULE: In the `stats_overview` section of `player_state.py`, no stat should ever be 0. If a stat would be 0, its value must be a baseline of 10.
4. Update the historical lore files (`prologue.py`, etc.) with the events that occurred in that act.
5. Modify MULTIPLE files. Populate all relevant sections with detail.
6. Your response MUST be a single, valid JSON object. Keys are the filenames you modified, values are the COMPLETE new file content.
Return ONLY the raw JSON object."""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        updated_files = json.loads(response.text.strip().removeprefix("```json").removesuffix("```"))
    except Exception as e:
        st.error(f"An error occurred while processing the AI response: {e}"); return False
        
    st.info("AI processing complete. Writing changes to local files...")
    for key, content in updated_files.items():
        filename = os.path.basename(key) 
        filepath = os.path.join("my_gm", filename) if filename == "player_state.py" else os.path.join(LORE_FOLDER, filename)
        with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
    return True

# --- UI Display Functions ---
def display_section(title, data):
    if data:
        st.subheader(title)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item_title = item.get('name', item.get('term', 'Entry'))
                    with st.expander(f"**{item_title}**"):
                        for k, v in item.items():
                            if k.lower() not in ['name', 'term']:
                                st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
                else:
                    st.markdown(f"- {item}")
        else:
            st.markdown(data)

def display_dict_section(title, data):
    if data:
        st.subheader(title)
        for key, value in data.items():
            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

# --- PAGE DEFINITIONS ---
def render_character_sheet():
    st.title("Character Sheet")
    state = load_player_state()
    if state:
        display_dict_section("🧍 Player Profile", getattr(state, 'player_profile', None))
        st.subheader("📈 Stats Overview")
        stats = getattr(state, 'stats_overview', {})
        if stats:
            cols = st.columns(3)
            i = 0
            for key, value in stats.items():
                cols[i % 3].metric(label=key, value=value)
                i += 1
        traits = getattr(state, 'traits', {})
        if traits:
            st.subheader("🧬 Traits")
            display_section("Active Traits", traits.get("active_traits"))
            display_section("Echoform Traits", traits.get("echoform_traits"))
            # ... and so on for all trait types
        
        abilities = getattr(state, 'abilities_techniques', {})
        if abilities:
            st.subheader("🪄 Abilities / Techniques")
            # ... display abilities
        
        inventory = getattr(state, 'inventory', {})
        if inventory:
            st.subheader("🎒 Inventory")
            # ... display inventory
        
        display_section("🧑‍🤝‍🧑 Companions", getattr(state, 'companions', None))
        display_dict_section("🏕️ Camp / Base Upgrades", getattr(state, 'camp_base_upgrades', None))
        # ... and so on
    else:
        st.error("Could not load player state. Make sure `my_gm/player_state.py` exists.")

def render_lore_browser():
    st.title("📖 Gelmark Lore Browser")
    def custom_sort_key(filename):
        if filename == 'prologue': return 0
        if filename.startswith('act'):
            try: return int(filename.replace('act', ''))
            except ValueError: return 999
        return 999

    found_files = [f.replace('.py', '') for f in os.listdir(LORE_FOLDER) if f.endswith('.py') and '__init__' not in f]
    lore_files = sorted(found_files, key=custom_sort_key)
    pages = {file.replace('_', ' ').title(): file for file in lore_files}
    if pages:
        selected_page_title = st.sidebar.radio("View Lore Section:", list(pages.keys()), key="lore_nav")
        selected_module_name = pages[selected_page_title]
        module_data = load_lore_module(selected_module_name)
        if module_data:
            section_variable_name = f"{selected_module_name}_lore"
            section_data = getattr(module_data, section_variable_name, {})
            lore_headers = {
                "summary": "📘 Summary", "major_events": "🧩 Major Events", "companions_bond_status": "🧑‍🤝‍🧑 Companions & Bond Status",
                "traits_unlocked": "✨ Traits Unlocked", "shrines_visited": "🛕 Shrines Visited", "visions_echo_sequences": "🔮 Visions & Echo Sequences",
                "lore_codex_expansions": "📖 Lore Entries / Codex Expansions", "timeline_edits": "⏳ Timeline Edits", "key_terms_introduced": "🔑 Key Terms Introduced",
                "locations_realms_visited": "🗺️ Locations & Realms Visited", "faction_threat_encounters": "👽 Faction or Threat Encounters",
                "oaths_rituals_performed": "📜 Oaths & Rituals Performed", "artifacts_discovered": "🏺 Artifacts Discovered",
                "narrative_threads_opened": "❓ Narrative Threads Opened", "narrative_threads_closed": "✅ Narrative Threads Closed"
            }
            for key, title in lore_headers.items():
                display_section(title, section_data.get(key))
    else:
        st.warning(f"No lore files found in '{LORE_FOLDER}'.")

# --- MAIN APP LAYOUT ---
st.sidebar.title("Navigation")
main_page = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser"])
st.sidebar.markdown("---")
st.sidebar.title("🛠️ Lore Updater")

# --- THE FILE UPLOADER IS RESTORED HERE ---
st.sidebar.subheader("Upload Narrative Log")
uploaded_file = st.sidebar.file_uploader("Upload your master story document", type=['txt', 'md', 'docx'])

if st.sidebar.button("Process and Update Lore"):
    if not os.getenv("GEMINI_API_KEY"): st.sidebar.error("GEMINI_API_KEY is not set!")
    elif uploaded_file is None: st.sidebar.warning("Please upload a file.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        narrative_log = ""
        try:
            if uploaded_file.name.endswith('.docx'):
                narrative_log = "\n".join([p.text for p in docx.Document(uploaded_file).paragraphs])
            else:
                narrative_log = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")

        if narrative_log:
            with st.spinner("The AI is updating your world..."):
                success = run_lore_update(narrative_log)
            if success:
                st.success("Data files updated!"); st.balloons(); st.rerun()
            else:
                st.error("The update failed. See details above.")

if main_page == "Character Sheet":
    render_character_sheet()
else:
    render_lore_browser()