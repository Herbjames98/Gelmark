import streamlit as st
import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
import importlib.util

# --- Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

# --- Paths ---
LORE_FOLDER = os.path.join(SCRIPT_DIR, "my_gm", "lore_modules")
PLAYER_STATE_FILE = os.path.join(SCRIPT_DIR, "my_gm", "player_state.py")
MEMORY_FILE = os.path.join(SCRIPT_DIR, "my_gm", "memory_bank.json")

# --- Utility Functions ---
def load_module_from_file(filepath):
    try:
        if not os.path.exists(filepath): return None
        module_name = f"loader_{os.path.basename(filepath)}_{os.path.getmtime(filepath)}"
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        st.error(f"Error loading `{filepath}`: {e}")
        return None

def load_memory_log():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_memory_log(log):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)
    except Exception as e:
        st.error(f"Error saving memory log: {e}")

# --- AI Engine ---
def run_ai_update(narrative_log):
    st.info("🧠 Processing with Gemini 2.5...")

    memory_log = load_memory_log()
    past_memories = "\n".join(f"[{m['timestamp']}] {m['summary']}" for m in memory_log[-5:])

    file_snapshots = {}
    if os.path.exists(PLAYER_STATE_FILE):
        with open(PLAYER_STATE_FILE, 'r', encoding='utf-8') as f:
            file_snapshots["player_state.py"] = f.read()
    if os.path.exists(LORE_FOLDER):
        for fname in os.listdir(LORE_FOLDER):
            if fname.endswith(".py") and "__init__" not in fname:
                with open(os.path.join(LORE_FOLDER, fname), "r", encoding="utf-8") as f:
                    file_snapshots[fname] = f.read()

    prompt = f"""
You are a Gemini 2.5 historian AI maintaining structured game files.

<narrative_log>
{narrative_log}
</narrative_log>

<past_memories>
{past_memories}
</past_memories>

<game_files>
{''.join([f'--- {fn} ---\n{content}\n\n' for fn, content in file_snapshots.items()])}
</game_files>

Your job:
1. Update any traits, companions, inventory, or events.
2. Merge "Grace" and "G.R.A.C.E." entries.
3. Provide valid updated Python file(s) in this format: {{ "filename.py": "FULL FILE CONTENT" }}.
4. After the JSON, give a short memory summary (2–3 lines) of this update.

Respond only in raw JSON + memory summary. No Markdown formatting.
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        full_text = response.text.strip().removeprefix("```json").removesuffix("```")

        split_point = full_text.rfind("}") + 1
        file_json = full_text[:split_point]
        summary_text = full_text[split_point:].strip()

        updated_files = json.loads(file_json)

    except Exception as e:
        st.error(f"Gemini failed: {e}")
        st.code(response.text if 'response' in locals() else "No response.")
        return False

    for fname, code in updated_files.items():
        dst = os.path.join(SCRIPT_DIR, "my_gm", fname) if fname == "player_state.py" else os.path.join(LORE_FOLDER, fname)
        try:
            with open(dst, "w", encoding="utf-8") as f:
                f.write(code)
            st.success(f"✅ Updated `{fname}`.")
        except Exception as e:
            st.error(f"❌ Failed to write `{fname}`: {e}")

    if summary_text:
        memory_log.append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M'),
            "summary": summary_text
        })
        save_memory_log(memory_log)

    return True

# --- Display Functions ---
def display_section(title, data):
    if not data: return
    st.subheader(title)
    if isinstance(data, list):
        for item in data:
            with st.expander(f"🔹 {item.get('name', 'Unnamed')}"):
                st.markdown(f"*{item.get('description', '')}*")
                for k, v in item.items():
                    if k not in ['name', 'description']:
                        st.markdown(f"**{k.title()}:** {v}")
    elif isinstance(data, dict):
        for k, v in data.items():
            st.markdown(f"**{k.title()}:** {v}")

def render_character_sheet():
    st.title("📜 Character Sheet")
    state = load_module_from_file(PLAYER_STATE_FILE)
    if not state:
        st.error("Could not load character sheet. Check if `player_state.py` is valid.")
        return

    display_section("🧍 Profile", getattr(state, "player_profile", {}))
    display_section("📊 Stats", getattr(state, "stats_overview", {}))
    traits = getattr(state, "traits", {})
    display_section("✨ Active Traits", traits.get("active_traits"))
    display_section("🔮 Echoform Traits", traits.get("echoform_traits"))
    display_section("🧬 Hybrid/Fusion Traits", traits.get("hybrid_fusion_traits"))
    inv = getattr(state, "inventory", {})
    display_section("🎒 Artifacts", inv.get("artifacts_relics"))
    display_section("🔑 Key Items", inv.get("key_items"))
    display_section("🛡️ Equipment", inv.get("equipment"))
    display_section("🧑‍🤝‍🧑 Companions", getattr(state, "companions", []))

def render_lore_browser():
    st.title("📖 Gelmark Lore Browser")
    if not os.path.exists(LORE_FOLDER): return st.warning("Missing lore folder.")
    lore_files = sorted(f[:-3] for f in os.listdir(LORE_FOLDER) if f.endswith(".py"))
    if not lore_files: return st.info("No lore files found.")
    selected = st.sidebar.radio("Select Lore Section:", lore_files)
    module = load_module_from_file(os.path.join(LORE_FOLDER, selected + ".py"))
    if module:
        display_section("📘 Summary", getattr(module, f"{selected}_lore", {}).get("summary"))
        display_section("🧩 Major Events", getattr(module, f"{selected}_lore", {}).get("major_events"))

def render_play_game_page():
    st.title("🎲 Play the Game")
    st.info("Gameplay not yet implemented.")

# --- UI ---
st.sidebar.title("Navigation")
main_page = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser", "Play the Game"])
st.sidebar.subheader("🛠 Lore Updater")
log_input = st.sidebar.text_area("Paste narrative log here:", height=200)

if st.sidebar.button("Update Lore"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("Missing `GEMINI_API_KEY` in .env.")
    elif not log_input.strip():
        st.sidebar.error("Please enter narrative text.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("Processing lore..."):
            if run_ai_update(log_input):
                st.success("✅ Lore updated.")
                st.balloons(); st.rerun()
            else:
                st.error("❌ Update failed.")

# Render page
if main_page == "Character Sheet":
    render_character_sheet()
elif main_page == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()
