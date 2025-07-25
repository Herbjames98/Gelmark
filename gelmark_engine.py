import streamlit as st
import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
import importlib.util

# --- Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(dotenv_path=DOTENV_PATH)

# --- Paths ---
LORE_FOLDER = os.path.join(SCRIPT_DIR, "my_gm", "lore_modules")
PLAYER_STATE_FILE = os.path.join(SCRIPT_DIR, "my_gm", "player_state.py")
MEMORY_FILE = os.path.join(SCRIPT_DIR, "my_gm", "memory_bank.json")

# --- Util Functions ---
def load_module_from_file(filepath):
    try:
        if not os.path.exists(filepath): return None
        module_name = f"loader_{os.path.basename(filepath)}_{os.path.getmtime(filepath)}"
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        st.error(f"Error loading data from {filepath}: {e}")
        return None

def load_memory_log():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_memory_log(memory_log):
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory_log, f, indent=2)
    except Exception as e:
        st.error(f"Failed to save memory: {e}")

# --- AI Update Flow ---
def run_ai_update(narrative_log):
    st.info("Contacting the Gemini AI and updating memory...")

    # 1. Load all game files
    all_content = {}
    if os.path.exists(PLAYER_STATE_FILE):
        with open(PLAYER_STATE_FILE, 'r', encoding='utf-8') as f:
            all_content["player_state.py"] = f.read()
    if os.path.exists(LORE_FOLDER):
        for filename in os.listdir(LORE_FOLDER):
            if filename.endswith('.py') and '__init__' not in filename:
                path = os.path.join(LORE_FOLDER, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    all_content[filename] = f.read()

    data_string = "\n\n".join([f"--- File: {n} ---\n{c}" for n, c in all_content.items()])

    # 2. Load prior memory context
    memory_log = load_memory_log()
    past_memories = "\n".join(f"[{m['timestamp']}]: {m['summary']}" for m in memory_log[-5:])

    # 3. AI Prompt with memory context
    prompt = f"""
You are a lore historian AI inside a roleplaying engine.

<current_narrative>
{narrative_log}
</current_narrative>

<past_memory>
{past_memories}
</past_memory>

<files>
{data_string}
</files>

Instructions:
1. Update `player_state.py` and all lore files based on the log.
2. Merge duplicates like "Grace" and "G.R.A.C.E."
3. Output as JSON in this format: {{ "filename.py": "full_code_as_string" }}
4. Add vivid descriptions and narrative metadata where needed.
5. Do not wrap the response in Markdown.

After updates, also summarize the log into 2-3 sentences (to be stored in memory).
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")  # adjust if needed
        response = model.generate_content(prompt)
        text = response.text.strip().removeprefix("```json").removesuffix("```")
        updated_files = json.loads(text)
    except Exception as e:
        st.error(f"AI error: {e}")
        st.code(response.text if 'response' in locals() else "No response from AI.")
        return False

    # 4. Write updated files
    for key, content in updated_files.items():
        fn = os.path.basename(key)
        dst = os.path.join(SCRIPT_DIR, "my_gm", fn) if fn == "player_state.py" else os.path.join(LORE_FOLDER, fn)
        try:
            with open(dst, 'w', encoding='utf-8') as f: f.write(content)
            st.write(f"✅ Updated `{fn}`.")
        except Exception as e:
            st.error(f"Write failed for `{fn}`: {e}")
            return False

    # 5. Store memory summary
    try:
        memory_log.append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M'),
            "summary": narrative_log[:300].replace('\n', ' ') + "..."
        })
        save_memory_log(memory_log)
    except Exception as e:
        st.warning(f"Couldn't save summary to memory: {e}")

    return True

# --- Display Utilities ---
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
            st.markdown(f"**{k.replace('_',' ').title()}:** {v}")

# --- Pages ---
def render_character_sheet():
    st.title("Character Sheet")
    player_module = load_module_from_file(PLAYER_STATE_FILE)
    if not player_module:
        st.error("Could not load character sheet. Check if `player_state.py` is valid.")
        return

    display_dict_section("🧍 Player Profile", getattr(player_module, "player_profile", {}))
    st.subheader("📈 Stats Overview")
    stats = getattr(player_module, "stats_overview", {})
    cols = st.columns(3)
    for i, (k, v) in enumerate(stats.items()):
        cols[i % 3].metric(label=k, value=v)

    traits = getattr(player_module, "traits", {})
    st.subheader("🧬 Traits")
    display_section("Active Traits", traits.get("active_traits"))
    display_section("Echoform Traits", traits.get("echoform_traits"))
    display_section("Hybrid/Fusion Traits", traits.get("hybrid_fusion_traits"))

    inventory = getattr(player_module, "inventory", {})
    st.subheader("🎒 Inventory")
    display_section("Artifacts / Relics", inventory.get("artifacts_relics"))
    display_section("Key Items", inventory.get("key_items"))

    equipment = inventory.get("equipment", {})
    if equipment:
        st.subheader("🛡️ Equipment")
        for slot, item in equipment.items():
            st.markdown(f"**{slot.title()}:**")
            st.markdown(f"🔸 **{item.get('name', 'Unnamed')}**: *{item.get('description', 'No description.')}*")

    def merge_duplicate_companions(companions):
        merged = {}
        if not isinstance(companions, list): return []
        for comp in companions:
            key = comp.get("name", "").lower().replace(".", "")
            if key in merged:
                merged[key].update({k: v for k, v in comp.items() if v})
            else:
                merged[key] = comp
        return list(merged.values())

    display_section("🧑‍🤝‍🧑 Companions", merge_duplicate_companions(getattr(player_module, "companions", [])))

def render_lore_browser():
    st.title("📖 Gelmark Lore Browser")
    if not os.path.exists(LORE_FOLDER): return st.warning("Missing lore folder.")

    def sort_key(n): return 0 if n == 'prologue' else int(n.replace('act','')) if n.startswith('act') else 999
    files = sorted([f[:-3] for f in os.listdir(LORE_FOLDER) if f.endswith('.py')], key=sort_key)
    pages = {n.replace('_', ' ').title(): n for n in files}

    if not pages: return st.info("No lore found.")
    sel = st.sidebar.radio("View Lore Section:", list(pages.keys()))
    module = load_module_from_file(os.path.join(LORE_FOLDER, pages[sel] + ".py"))
    if module:
        data = getattr(module, f"{pages[sel]}_lore", {})
        for key, title in {
            "summary": "📘 Summary", "major_events": "🧩 Major Events"
        }.items():
            display_section(title, data.get(key))

def render_play_game_page():
    st.title("🎲 Play the Game")
    st.info("Under construction.")

# --- Main App ---
st.sidebar.title("Navigation")
main = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser", "Play the Game"])
st.sidebar.markdown("---")
st.sidebar.subheader("🛠 Lore Updater")
narrative = st.sidebar.text_area("Paste narrative log here:", height=200)

if st.sidebar.button("Process and Update Lore"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("GEMINI_API_KEY missing in .env")
    elif not narrative:
        st.sidebar.error("Paste narrative log first.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("Updating world files…"):
            if run_ai_update(narrative):
                st.success("Lore updated successfully!")
                st.balloons(); st.rerun()
            else:
                st.error("Update failed. See error logs.")

if main == "Character Sheet":
    render_character_sheet()
elif main == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()
