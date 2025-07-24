# This is the Gelmark Engine: The definitive, fully automated version.
# It uses the correct Gemini 1.5 Pro model, reads/writes all data files,
# and is programmed to generate and display detailed descriptions.

import streamlit as st
import os
import json
import ast
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
    st.info("Preparing lore and contacting the Gemini AI...")
    all_content = {}
    if os.path.exists(PLAYER_STATE_FILE):
        with open(PLAYER_STATE_FILE, 'r', encoding='utf-8') as f: all_content["player_state.py"] = f.read()
    if os.path.exists(LORE_FOLDER):
        for filename in os.listdir(LORE_FOLDER):
            if filename.endswith('.py') and '__init__' not in filename:
                filepath = os.path.join(LORE_FOLDER, filename)
                with open(filepath, 'r', encoding='utf-8') as f: all_content[filename] = f.read()

    data_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in all_content.items()])
    prompt = f"""You are a meticulous historian AI tasked with updating structured game data from a narrative log.
<log>{narrative_log}</log>

GAME FILES: <code>{data_string}</code>

Instructions:
1. For `player_state.py`, ensure every trait, item, companion, and relic is represented as a dictionary with:
    - "name": the official label
    - "description": a vivid, lore-rich explanation of what it is
    - optional metadata like "status"
2. Keep all content in valid Python syntax, wrapped in a JSON object: {{ filename: full_file_content }}
3. Avoid repeating names. Merge duplicate companions like "Grace" and "G.R.A.C.E."

Return ONLY the raw JSON object (no Markdown, no explanations).
"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        updated_files = ast.literal_eval(response.text.strip().removeprefix("```json").removesuffix("```"))
    except Exception as e:
        st.error(f"Error processing AI response: {e}")
        st.subheader("Raw AI Response:")
        st.code(response.text if 'response' in locals() else "No response from AI.", language="text")
        return False

    st.info("Writing changes to files...")
    for key, content in updated_files.items():
        content = "\n".join(
            [f"# {line}" if line.strip().startswith("--- File: ") else line for line in content.splitlines()]
        )
        fn = os.path.basename(key)
        dst = os.path.join(SCRIPT_DIR, fn) if fn == "player_state.py" else os.path.join(LORE_FOLDER, fn)
        try:
            with open(dst, 'w', encoding='utf-8') as f: f.write(content)
            st.write(f"✅ Updated `{fn}`.")
        except Exception as e:
            st.error(f"Failed to write `{fn}`: {e}")
            return False
    return True

# --- UI FUNCTIONS ---
def display_section(title, data):
    if data:
        st.subheader(title)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    name = item.get("name", "Unnamed")
                    desc = item.get("description", "")
                    with st.expander(f"🔹 {name}"):
                        if desc:
                            st.markdown(f"*{desc}*")
                        for k, v in item.items():
                            if k not in ['name', 'description']:
                                st.markdown(f"**{k.replace('_',' ').title()}:** {v}")
                else:
                    st.markdown(f"- {item}")
        else:
            st.markdown(data)

def display_dict_section(title, data):
    if data:
        st.subheader(title)
        for k, v in data.items():
            st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")

def render_character_sheet():
    st.title("Character Sheet")
    player_data = load_data_from_file(PLAYER_STATE_FILE, "PLAYER_STATE")
    if not player_data:
        st.error("Could not load character sheet.")
        return

    display_dict_section("🧍 Player Profile", player_data.get("profile"))
    st.subheader("📈 Stats Overview")
    stats = player_data.get("stats", {})
    cols = st.columns(3)
    for i, (k, v) in enumerate(stats.items()):
        cols[i % 3].metric(label=k, value=v)

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

    def merge_duplicate_companions(companions):
        merged = {}
        for comp in companions:
            key = comp['name'].strip().lower().replace(".", "")
            if key in merged:
                for k, v in comp.items():
                    if v and not merged[key].get(k):
                        merged[key][k] = v
                merged[key]['name'] = "G.R.A.C.E." if key == "grace" else comp['name']
            else:
                merged[key] = comp
        return list(merged.values())

    raw_companions = player_data.get("companions", [])
    display_section("🧑‍🤝‍🧑 Companions", merge_duplicate_companions(raw_companions))

def render_lore_browser():
    st.title("📖 Gelmark Lore Browser")
    def sort_key(n): return 0 if n == 'prologue' else int(n.replace('act','')) if n.startswith('act') else 999
    if not os.path.exists(LORE_FOLDER): st.warning("Missing lore_modules folder."); return
    files = sorted([f[:-3] for f in os.listdir(LORE_FOLDER) if f.endswith('.py') and '__init__' not in f], key=sort_key)
    pages = {n.title(): n for n in files}
    sel = st.sidebar.radio("View Lore Section:", list(pages.keys()), key="lore_nav")
    data = load_data_from_file(os.path.join(LORE_FOLDER, pages[sel] + ".py"), f"{pages[sel]}_lore")
    if data:
        for k, t in {"summary":"📘 Summary", "major_events":"🧩 Major Events"}.items():
            display_section(t, data.get(k))

def render_play_game_page():
    st.title("🎲 Play the Game")
    st.info("Under construction.")

# --- MAIN UI ---
st.sidebar.title("Navigation")
main = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser", "Play the Game"])
st.sidebar.markdown("---")
st.sidebar.subheader("🛠 Lore Updater")
narrative = st.sidebar.text_area("Paste narrative log here:", height=200)

if st.sidebar.button("Process and Update Lore"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("GEMINI_API_KEY missing in .env")
    elif not narrative:
        st.sidebar.error("Please paste a narrative log.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("Updating world files…"):
            if run_ai_update(narrative):
                st.success("Lore updated successfully!")
                st.balloons(); st.rerun()
            else:
                st.error("Update failed. Check errors above.")

if main == "Character Sheet":
    render_character_sheet()
elif main == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()
