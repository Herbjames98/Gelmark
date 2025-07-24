# This is the Gelmark Engine V3: a single, self-contained application.
# It is now "self-aware" and will always find the .env file correctly.

import streamlit as st
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import importlib.util

# --- THIS IS THE BULLETPROOF FIX ---
# 1. Find the absolute path of the directory where this script is located.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Build the full path to the .env file, which is in the same directory.
DOTENV_PATH = os.path.join(SCRIPT_DIR, '.env')

# 3. Load the secret key from that specific, absolute path.
load_dotenv(dotenv_path=DOTENV_PATH)
# --- END OF FIX ---

# --- Configuration (Paths are now absolute and reliable) ---
st.set_page_config(page_title="Gelmark Engine", layout="wide")
# All other paths are now built from the script's location, making them reliable.
LORE_FOLDER = os.path.join(SCRIPT_DIR, "lore_modules")
PLAYER_STATE_FILE = os.path.join(SCRIPT_DIR, "player_state.py")


# --- GAME DATABASE (We now load data from external files) ---

def load_data_from_file(filepath, variable_name):
    """Loads a specific dictionary variable from a Python file."""
    try:
        if not os.path.exists(filepath):
            # This is not an error, the file just might not exist yet.
            return {}
        
        # Use a unique module name to prevent caching issues
        module_name_unique = f"data_loader_{variable_name}_{os.path.getmtime(filepath)}"
        spec = importlib.util.spec_from_file_location(module_name_unique, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, variable_name, {})
    except Exception as e:
        st.error(f"Error loading data from {filepath}: {e}")
        return {}

# Load the data at the start of the script
PLAYER_STATE = load_data_from_file(PLAYER_STATE_FILE, "player_profile") # Assuming the main var is player_profile
# We can add a similar loader for LORE_DATA if we move it to its own file.


# --- AI UPDATER FUNCTION ---

def run_ai_update(narrative_log):
    """Generates the updated Python code and writes it to the files."""
    st.info("Preparing lore and contacting the Gemini AI...")
    
    # This now uses the safe, absolute paths
    all_content = {}
    if os.path.exists(PLAYER_STATE_FILE):
        with open(PLAYER_STATE_FILE, 'r', encoding='utf-8') as f:
            all_content['player_state.py'] = f.read()
    for filename in os.listdir(LORE_FOLDER):
        if filename.endswith('.py') and '__init__' not in filename:
            filepath = os.path.join(LORE_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                all_content[filename] = f.read()
    
    data_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in all_content.items()])

    prompt = f"""You are a meticulous historian AI. Your task is to update the Python dictionaries containing the game's data based on a new narrative log.
NARRATIVE LOG: <log>{narrative_log}</log>
CURRENT GAME DATA: <code>{data_string}</code>
INSTRUCTIONS:
1. Read the new narrative log and the current game data.
2. Generate the complete, updated Python code for ALL relevant files (`player_state.py`, `act1.py`, etc.).
3. Be exhaustive. Update stats, inventory, traits, companion statuses, and add historical events to the correct acts.
4. Your response MUST be a single, valid JSON object where keys are filenames and values are the complete new file content.
Return ONLY the raw JSON object."""
    
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        updated_files = json.loads(response.text.strip().removeprefix("```json").removesuffix("```"))
    except Exception as e:
        st.error(f"An error occurred while processing the AI response: {e}")
        st.subheader("Raw AI Response:")
        st.code(response.text if 'response' in locals() else "No response from AI.", language="text")
        return False
        
    st.info("AI processing complete. Writing changes to local files...")
    for key, content in updated_files.items():
        filename = os.path.basename(key)
        filepath = os.path.join(SCRIPT_DIR, filename) if filename == "player_state.py" else os.path.join(LORE_FOLDER, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    return True


# --- UI DISPLAY FUNCTIONS ---
# (These are unchanged)
def display_section(title, data):
    if data:
        st.subheader(title)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    with st.expander(f"**{item.get('name', item.get('term', 'Entry'))}**"):
                        for k, v in item.items():
                            if k.lower() not in ['name', 'term']: st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
                else: st.markdown(f"- {item}")
        else: st.markdown(data)

def display_dict_section(title, data):
    if data:
        st.subheader(title)
        for key, value in data.items(): st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

# --- PAGE DEFINITIONS ---

def render_character_sheet():
    st.title("Character Sheet")
    # Load the player state dynamically
    player_data = load_data_from_file(PLAYER_STATE_FILE, "player_profile")
    if not player_data:
        st.error("Could not load character sheet. Make sure `player_state.py` exists and is in the same folder as the main script.")
        return

    display_dict_section("🧍 Player Profile", player_data)
    # The rest of the page would load other variables from player_state.py
    

def render_lore_browser():
    st.title("📖 Gelmark Lore Browser")
    st.info("Lore browser is under construction.")


def render_play_game_page():
    st.title("🎲 Play the Game")
    st.info("The 'Play the Game' feature is under construction.")

# --- MAIN APP LAYOUT ---
st.sidebar.title("Navigation")
main_page = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser", "Play the Game"])
st.sidebar.markdown("---")
st.sidebar.title("🛠️ Lore Updater")
st.sidebar.subheader("Generate Updated Lore")
narrative_log_input = st.sidebar.text_area("Paste your new story information here:", height=200)

if st.sidebar.button("Generate Update Code"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("GEMINI_API_KEY is not set! Check your .env file and its location.")
    elif not narrative_log_input:
        st.sidebar.warning("Please paste a narrative log.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("The AI is generating your updated lore..."):
            success = run_ai_update(narrative_log_input)
        
        if success:
            st.success("Lore files updated successfully! The page will now reload.")
            st.balloons()
            st.rerun()
        else:
            st.error("The lore update failed. See the error message above.")


if main_page == "Character Sheet":
    render_character_sheet()
elif main_page == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()