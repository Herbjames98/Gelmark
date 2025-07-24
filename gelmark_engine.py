# This is the Gelmark Engine: The definitive, fully automated version.
# It uses the correct Gemini 1.5 Pro model and reads/writes all data files.

import streamlit as st
import os
import json
import ast  # ✅ Added for safe AI response parsing
import google.generativeai as genai
from dotenv import load_dotenv
import importlib.util

# --- Bulletproof .env loading ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(dotenv_path=DOTENV_PATH)

# --- Configuration ---
st.set_page_config(page_title="Gelmark Engine", layout="wide")
LORE_FOLDER = os.path.join(SCRIPT_DIR, "lore_modules")
PLAYER_STATE_FILE = os.path.join(SCRIPT_DIR, "player_state.py")

# --- CORE DATA & AI FUNCTIONS ---

def load_data_from_file(filepath, variable_name):
    """Loads a specific dictionary variable from a Python file."""
    try:
        if not os.path.exists(filepath): return {}
        module_name_unique = f"loader_{variable_name}_{os.path.getmtime(filepath)}"
        spec = importlib.util.spec_from_file_location(module_name_unique, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, variable_name, {})
    except Exception as e:
        st.error(f"Error loading data from {filepath}: {e}")
        return {}

def run_ai_update(narrative_log):
    """The main AI logic function that now writes directly to files."""
    st.info("Preparing lore and contacting the Gemini AI...")
    
    all_content = {}
    if os.path.exists(PLAYER_STATE_FILE):
        with open(PLAYER_STATE_FILE, 'r', encoding='utf-8') as f:
            all_content['player_state.py'] = f.read()
    if os.path.exists(LORE_FOLDER):
        for filename in os.listdir(LORE_FOLDER):
            if filename.endswith('.py') and '__init__' not in filename:
                filepath = os.path.join(LORE_FOLDER, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    all_content[filename] = f.read()
    
    data_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in all_content.items()])

    prompt = f"""You are a meticulous historian AI. Your task is to update a complete set of game data files based on a new narrative log.
NARRATIVE LOG: <log>{narrative_log}</log>
GAME DATA FILES: <code>{data_string}</code>
INSTRUCTIONS:
1. Read the new narrative log.
2. Update `player_state.py` to reflect the player's MOST RECENT status.
3. Update the historical lore files (`prologue.py`, etc.) with events from that act.
4. Your response MUST be a single, valid JSON object where keys are the filenames you modified and values are the COMPLETE new file content.
Return ONLY the raw JSON object."""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text.strip().removeprefix("```json").removesuffix("```")

        # ✅ Use ast.literal_eval to handle Python-style responses
        updated_files = ast.literal_eval(response_text)

    except Exception as e:
        st.error(f"An error occurred while processing the AI response: {e}")
        st.subheader("Raw AI Response:")
        st.code(response.text if 'response' in locals() else "No response from AI.", language="text")
        return False

    st.info("AI processing complete. Writing changes to local files...")
    for key, content in updated_files.items():
        # 💡 Auto-comment invalid Python headers like --- File: xyz.py ---
        content = "\n".join(
            [f"# {line}" if line.strip().startswith("--- File: ") else line for line in content.splitlines()]
        )

        filename = os.path.basename(key)
        filepath = os.path.join(SCRIPT_DIR, filename) if filename == "player_state.py" else os.path.join(LORE_FOLDER, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            st.write(f"✅ Updated `{filename}`.")
        except Exception as e:
            st.error(f"Failed to write to `{filename}`: {e}")
            return False
    return True

# --- UI DISPLAY & PAGE RENDERING FUNCTIONS ---
def display_section(title, data):
    if data:
        st.subheader(title)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    with st.expander(f"**{item.get('name', item.get('term', 'Entry'))}**"):
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

def render_character_sheet():
    st.title("Character Sheet")
    player_data = load_data_from_file(PLAYER_STATE_FILE, "PLAYER_STATE")
    if not player_data:
        st.error("Could not load character sheet. Check player_state.py.")
        return
    display_dict_section("🧍 Player Profile", player_data.get("profile"))
    st.subheader("📈 Stats Overview")
    cols = st.columns(3)
    i = 0
    for key, value in player_data.get("stats", {}).items():
        cols[i % 3].metric(label=key, value=value)
        i += 1
    traits = player_data.get("traits", {})
    st.subheader("🧬 Traits")
    display_section("Active", traits.get("active"))
    display_section("Echoform", traits.get("echoform"))
    display_section("Fused", traits.get("fused"))
    inventory = player_data.get("inventory", {})
    st.subheader("🎒 Inventory")
    display_section("Relics", inventory.get("relics"))
    display_section("Key Items", inventory.get("key_items"))
    display_dict_section("Equipment", inventory.get("equipment"))

    # ✅ Companion merge logic added here
    def merge_duplicate_companions(companions):
        merged = {}
        for comp in companions:
            name_key = comp['name'].strip().lower().replace(".", "")
            if name_key not in merged:
                merged[name_key] = comp
            else:
                for k, v in comp.items():
                    if v and (k not in merged[name_key] or not merged[name_key][k]):
                        merged[name_key][k] = v
                merged[name_key]['name'] = "G.R.A.C.E." if name_key == "grace" else comp['name']
        return list(merged.values())

    companions_raw = player_data.get("companions", [])
    merged_companions = merge_duplicate_companions(companions_raw)
    display_section("🧑‍🤝‍🧑 Companions", merged_companions)


def render_lore_browser():
    st.title("📖 Gelmark Lore Browser")
    def custom_sort_key(filename_no_ext):
        if filename_no_ext == 'prologue': return 0
        if filename_no_ext.startswith('act'):
            try: return int(filename_no_ext.replace('act', ''))
            except ValueError: return 999
        return 999

    if not os.path.exists(LORE_FOLDER):
        st.warning("The 'lore_modules' folder was not found.")
        return
    found_files = [f.replace('.py', '') for f in os.listdir(LORE_FOLDER) if f.endswith('.py') and '__init__' not in f]
    lore_files = sorted(found_files, key=custom_sort_key)
    pages = {file.replace('_', ' ').title(): file for file in lore_files}
    if pages:
        selected_page_title = st.sidebar.radio("View Lore Section:", list(pages.keys()), key="lore_nav")
        selected_module_name = pages[selected_page_title]
        section_data = load_data_from_file(os.path.join(LORE_FOLDER, f"{selected_module_name}.py"), f"{selected_module_name}_lore")
        if section_data:
            lore_headers = {"summary": "📘 Summary", "major_events": "🧩 Major Events"}  # Expand as needed
            for key, title in lore_headers.items():
                display_section(title, section_data.get(key))

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

if st.sidebar.button("Process and Update Lore"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("GEMINI_API_KEY is not set! Check your .env file.")
    elif not narrative_log_input:
        st.sidebar.warning("Please paste a narrative log.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("The AI is rewriting your world files..."):
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
