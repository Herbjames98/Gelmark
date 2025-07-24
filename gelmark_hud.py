# This is the definitive, three-page application.
# It now securely loads your API key from a .env file.

import streamlit as st
import os
import json
import google.generativeai as genai
import docx
import importlib.util
from dotenv import load_dotenv

# Load the secret key from the .env file
load_dotenv()

# --- Configuration and Setup ---
st.set_page_config(page_title="Gelmark Engine", layout="wide")
LORE_FOLDER = os.path.join("my_gm", "lore_modules")
PLAYER_STATE_FILE = os.path.join("my_gm", "player_state.py")

# --- CORE DATA & AI FUNCTIONS ---

def load_lore_module(module_name):
    # (The rest of the file is identical to our last working version)
    try:
        path = os.path.join(LORE_FOLDER, f"{module_name}.py")
        if not os.path.exists(path): return None
        module_name_unique = f"lore_module_{module_name}_{os.path.getmtime(path)}"
        spec = importlib.util.spec_from_file_location(module_name_unique, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        st.error(f"Error loading {module_name}: {e}"); return None

def load_player_state():
    try:
        if not os.path.exists(PLAYER_STATE_FILE): return None
        spec = importlib.util.spec_from_file_location("player_state", PLAYER_STATE_FILE)
        player_state_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(player_state_module)
        return player_state_module
    except Exception as e:
        st.error(f"Error loading player state: {e}"); return None

def get_all_game_data_as_string():
    all_content = {}
    if os.path.exists(PLAYER_STATE_FILE):
        with open(PLAYER_STATE_FILE, 'r', encoding='utf-8') as f:
            all_content['player_state.py'] = f.read()
    for filename in os.listdir(LORE_FOLDER):
        if filename.endswith('.py') and '__init__' not in filename:
            filepath = os.path.join(LORE_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                all_content[filename] = f.read()
    return "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in all_content.items()])

def run_lore_update(narrative_log, game_data_string):
    st.info("Preparing lore and contacting the Gemini AI...")
    prompt = f"""You are a meticulous and detail-oriented historian AI. Your task is to update a complete set of game data files based on a comprehensive narrative log. You must be exhaustive and leave no detail behind.
NARRATIVE LOG: <log>{narrative_log}</log>
GAME DATA FILES: <files>{game_data_string}</files>
YOUR UN-SKIPPABLE INSTRUCTIONS:
1.  **Analyze the Player's Final State:** Scrutinize the entire narrative log to determine the character's status AT THE END of the log. Update `player_state.py` with this final information.
    *   Stats: Update all numerical stats. If a stat is not mentioned, assume it has a baseline of 10.
    *   Inventory & Abilities: Meticulously list every single artifact, relic, key item, and piece of equipment mentioned. List all combat techniques, skills, and powers. DO NOT leave these sections empty if the information exists in the log.
    *   Companions: Update the status, sync %, and key events for all companions based on the final state of the log.
2.  **Analyze the Historical Lore:** Read the log chronologically from the beginning.
    *   For each event, identify which Act (Prologue, Act 1, Act 2, etc.) it belongs to.
    *   Populate the corresponding lore file for that Act (`prologue.py`, `act1.py`, etc.).
    *   Be detailed. Extract every "Major Event," "Artifact Discovered," "Trait Unlocked," etc., for each Act. You must populate MULTIPLE historical files.
3.  **Final Output:** Your response MUST be a single, valid JSON object. The keys must be ALL the filenames you have modified. The values must be the COMPLETE, new Python code content for each file. Do not summarize. Be verbose and comprehensive. Return ONLY the raw JSON object."""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        updated_files = json.loads(response.text.strip().removeprefix("```json").removesuffix("```"))
    except Exception as e:
        st.error(f"An error occurred while processing the AI response: {e}");
        st.subheader("Raw AI Response:")
        st.code(response.text if 'response' in locals() else "No response from AI.", language="text")
        return False
    st.info("Writing changes to local files...")
    for key, content in updated_files.items():
        filename = os.path.basename(key) 
        filepath = os.path.join("my_gm", filename) if filename == "player_state.py" else os.path.join(LORE_FOLDER, filename)
        with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
    return True
    
def run_cyoa_turn(chat_history, game_data_string):
    prompt = f"""You are the Game Master (GM) for the dark fantasy CYOA game, 'The Gelmark'. Your personality is immersive, detailed, and you adhere to the established canon.
CANON DATA (Your Memory): <canon>{game_data_string}</canon>
CURRENT SCENE SO FAR: <history>{chat_history}</history>
INSTRUCTIONS:
1. Read the Canon Data to understand the world, the player's current stats, traits, and story progress.
2. Read the Current Scene to understand the immediate context.
3. Based on the player's last action, continue the story in a compelling, literary style.
4. Your response must end with 2-4 clear, actionable choices for the player to make.
5. Do NOT break character or refer to yourself as an AI."""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while contacting the GM: {e}"

# --- UI DISPLAY & PAGE RENDERING FUNCTIONS ---
def display_section(title, data):
    # (Functions are unchanged)
    if data:
        st.subheader(title)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item_title = item.get('name', item.get('term', 'Entry'))
                    with st.expander(f"**{item_title}**"):
                        for k, v in item.items():
                            if k.lower() not in ['name', 'term']: st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
                else: st.markdown(f"- {item}")
        else: st.markdown(data)

def display_dict_section(title, data):
    if data:
        st.subheader(title)
        for key, value in data.items(): st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

def render_character_sheet():
    # (Page rendering is unchanged)
    st.title("Character Sheet")
    state = load_player_state()
    if state:
        display_dict_section("🧍 Player Profile", getattr(state, 'player_profile', None))
        st.subheader("📈 Stats Overview")
        stats = getattr(state, 'stats_overview', {})
        if stats:
            cols = st.columns(3)
            i = 0
            for key, value in stats.items(): cols[i % 3].metric(label=key, value=value); i += 1
        traits = getattr(state, 'traits', {});
        if traits:
            st.subheader("🧬 Traits")
            display_section("Active Traits", traits.get("active_traits"))
        abilities = getattr(state, 'abilities_techniques', {});
        if abilities: st.subheader("🪄 Abilities / Techniques"); display_section("Combat Techniques", abilities.get("combat_techniques"))
        inventory = getattr(state, 'inventory', {});
        if inventory: st.subheader("🎒 Inventory"); display_section("Artifacts / Relics", inventory.get("artifacts_relics"))
        display_section("🧑‍🤝‍🧑 Companions", getattr(state, 'companions', None))
        display_dict_section("🏕️ Camp / Base Upgrades", getattr(state, 'camp_base_upgrades', None))
    else: st.error("Could not load player state.")

def render_lore_browser():
    # (Page rendering is unchanged)
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
            lore_headers = {"summary": "📘 Summary", "major_events": "🧩 Major Events",} # (and so on)
            for key, title in lore_headers.items(): display_section(title, section_data.get(key))
    else: st.warning(f"No lore files found.")

def render_play_game_page():
    # (Page rendering is unchanged)
    st.title("🎲 Play the Game")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Welcome, Pulse-Bearer. The threads of fate are still. What would you like to do?"}]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    if prompt := st.chat_input("Your action..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("The world responds..."):
                game_data_string = get_all_game_data_as_string()
                chat_history = json.dumps(st.session_state.messages)
                response = run_cyoa_turn(chat_history, game_data_string)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- MAIN APP LAYOUT ---
st.sidebar.title("Navigation")
main_page = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser", "Play the Game"])
st.sidebar.markdown("---")
st.sidebar.title("🛠️ Lore Updater")
st.sidebar.subheader("Save Your Session")
narrative_log_input = st.sidebar.text_area("After playing, paste the session transcript here to update the lore:", height=150)
if st.sidebar.button("Process and Update Lore"):
    if not os.getenv("GEMINI_API_KEY"): st.sidebar.error("GEMINI_API_KEY is not set!")
    elif not narrative_log_input: st.sidebar.warning("Please paste a narrative log.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        game_data_string = get_all_game_data_as_string()
        with st.spinner("The AI is updating your world..."):
            success = run_lore_update(narrative_log_input, game_data_string)
        if success:
            st.success("Data files updated!"); st.balloons(); st.rerun()
        else:
            st.error("The update failed. See details above.")

if main_page == "Character Sheet":
    render_character_sheet()
elif main_page == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()