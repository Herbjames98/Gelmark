import streamlit as st
import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
import importlib.util
import ast
import re

# --- Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

# --- Paths ---
LORE_FOLDER = os.path.join(SCRIPT_DIR, "lore_modules")
PLAYER_STATE_FILE = os.path.join(SCRIPT_DIR, "player_state.py")
MEMORY_FILE = os.path.join(SCRIPT_DIR, "memory_bank.json")

# --- Utilities ---
def load_module_from_file(filepath):
    try:
        if not os.path.exists(filepath): return None
        module_name = f"loader_{os.path.basename(filepath)}_{time.time()}"
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        st.error(f"Error loading `{os.path.basename(filepath)}`: {e}")
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

# --- AI Integration ---
def apply_patches_with_ast(updated_files_patches):
    for fname, patches in updated_files_patches.items():
        dst = os.path.join(SCRIPT_DIR, fname) if fname == "player_state.py" else os.path.join(LORE_FOLDER, fname)
        
        source_code = ""
        # Create file if it doesn't exist, e.g., for a new Act
        if os.path.exists(dst):
            with open(dst, "r", encoding="utf-8") as f:
                source_code = f.read()

        try:
            tree = ast.parse(source_code)
            applied_patches = {var: False for var in patches}

            class Patcher(ast.NodeTransformer):
                def visit_Assign(self, node):
                    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                        var_name = node.targets[0].id
                        if var_name in patches:
                            try:
                                new_value_str = patches[var_name]
                                new_value_node = ast.parse(new_value_str, mode='eval').body
                                node.value = new_value_node
                                applied_patches[var_name] = True
                            except Exception as e:
                                st.warning(f"AST Patcher: Could not apply patch for '{var_name}' in `{fname}`. Malformed AI response? Error: {e}")
                    return node

            new_tree = Patcher().visit(tree)

            for var_name, applied in applied_patches.items():
                if not applied:
                    new_assignment_string = f"{var_name} = {patches[var_name]}"
                    try:
                        new_assign_node = ast.parse(new_assignment_string).body[0]
                        new_tree.body.append(new_assign_node)
                    except Exception as e:
                         st.error(f"❌ Failed to append new variable '{var_name}' to `{fname}`. The AI likely provided invalid Python syntax. Error: {e}")
                         st.code(new_assignment_string, language='python')
                         return False

            new_code = ast.unparse(new_tree)

            with open(dst, "w", encoding="utf-8") as f:
                f.write(new_code)
            st.success(f"✅ Securely patched `{fname}`.")

        except Exception as e:
            st.error(f"❌ Critical error patching `{fname}` with AST: {e}")
            st.code(source_code, language='python')
            return False
    return True

# --- MODIFIED SECTION ---
def run_ai_update(narrative_log):
    st.info("🧠 Processing with Gemini...")
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

    # CORRECTED PROMPT CONSTRUCTION
    # We build the game files string separately to avoid nested f-string issues.
    game_files_string = ''.join([f"--- {fn} ---\n{content}\n\n" for fn, content in file_snapshots.items()])

    # Now we build the final prompt using concatenation (+) instead of a single f-string.
    prompt = (
        "You are a meticulous Gemini AI historian maintaining structured Python game files.\n"
        "Based on the <narrative_log>, generate the necessary code changes for the <game_files>.\n\n"
        f"<narrative_log>{narrative_log}</narrative_log>\n"
        f"<past_memories>{past_memories}</past_memories>\n\n"
        "<game_files>\n"
        + game_files_string
        + "</game_files>\n\n"
        "Your job:\n"
        "1. Update traits, companions, inventory, or events.\n"
        "2. Merge \"Grace\" and \"G.R.A.C.E.\" into a single logical entry.\n"
        "3. Respond with a JSON object containing ONLY the Python variables that need changing. The value in the JSON must be a string containing a valid, single-line Python dict or list. Ensure the string uses single quotes for keys and values.\n"
        "4. If a new lore file is needed (e.g., for a new Act), create it.\n\n"
        "    Perfect response format:\n"
        "    ```json\n"
        "    {\n"
        '      "player_state.py": {\n'
        '        "companions": "[{\'name\': \'The Valking Captain\', \'description\': \'A formidable but now loyal ally.\'}]",\n'
        '        "traits": "{ \'active_traits\': [\'Rebirth\'], \'echoform_traits\': [], \'hybrid_fusion_traits\': []}"\n'
        '      },\n'
        '      "act3.py": {\n'
        '        "act3_lore": "{ \'summary\': \'A new act begins.\', \'major_events\': []}"\n'
        '      }\n'
        "    }\n"
        "    ```\n\n"
        "5. After the JSON block, give a short (2-3 line) memory summary of the update.\n"
        "Respond only in the raw JSON block + memory summary. No other text or explanations."
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        full_text = response.text.strip()
        
        json_str = full_text
        summary_text = ""
        
        if "```json" in full_text:
            match = re.search(r"```json\s*([\s\S]+?)\s*```", full_text)
            if match:
                json_str = match.group(1)
                summary_text = full_text[match.end():].strip()
        elif "}}" in full_text:
            split_point = full_text.rfind("}}") + 2
            json_str = full_text[:split_point]
            summary_text = full_text[split_point:].strip()

        updated_files_patches = json.loads(json_str)

    except Exception as e:
        st.error(f"Gemini response parsing failed: {e}")
        st.code(response.text if 'response' in locals() else "No response from AI.")
        return False

    if not apply_patches_with_ast(updated_files_patches):
        return False

    if summary_text:
        memory_log.append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M'),
            "summary": summary_text
        })
        save_memory_log(memory_log)

    return True
# --- END OF MODIFIED SECTION ---

# --- Display Utilities (No Changes) ---
def display_section(title, data):
    if not data: return
    st.subheader(title)
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                with st.expander(f"🔹 {item.get('name', 'Unnamed')}"):
                    st.markdown(f"*{item.get('description', '')}*")
                    for k, v in item.items():
                        if k not in ['name', 'description']:
                            st.markdown(f"**{k.replace('_',' ').title()}:** {v}")
            else:
                st.markdown(f"- {item}")
    elif isinstance(data, dict):
        for k, v in data.items():
            st.markdown(f"**{k.replace('_',' ').title()}:** {v}")

# --- Pages (No Changes) ---
def render_character_sheet():
    st.title("📜 Character Sheet")
    state = load_module_from_file(PLAYER_STATE_FILE)
    if not state:
        st.error("Could not load character sheet. Please check for errors or try updating the lore again.")
        return
    display_section("🧍 Profile", getattr(state, "player_profile", {}))
    st.subheader("📈 Stats Overview")
    stats = getattr(state, "stats_overview", {})
    cols = st.columns(3)
    for i, (k, v) in enumerate(stats.items()):
        cols[i % 3].metric(label=k, value=v)
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
    if not os.path.exists(LORE_FOLDER):
        return st.warning("Missing `lore_modules` folder.")
    def sort_key(n): return 0 if n == 'prologue' else int(n.replace('act', '')) if n.startswith('act') else 999
    lore_files = sorted([f[:-3] for f in os.listdir(LORE_FOLDER) if f.endswith(".py") and "__init__" not in f], key=sort_key)
    if not lore_files:
        return st.info("No lore files found.")
    sel = st.sidebar.radio("Select Lore Section:", lore_files, format_func=lambda x: x.replace("_", " ").title())
    mod = load_module_from_file(os.path.join(LORE_FOLDER, sel + ".py"))
    if mod:
        data = getattr(mod, f"{sel}_lore", {})
        display_section("📘 Summary", data.get("summary"))
        display_section("🧩 Major Events", data.get("major_events"))

def render_play_game_page():
    st.title("🎲 Play the Game")
    st.info("Gameplay module under construction.")

# --- Main UI (No Changes) ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser", "Play the Game"])
st.sidebar.subheader("🛠 Lore Updater")
log_input = st.sidebar.text_area("Paste narrative log here:", height=200)

if st.sidebar.button("Update Lore"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("Missing `GEMINI_API_KEY` in `.env`.")
    elif not log_input.strip():
        st.sidebar.error("Please enter a narrative log.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("Processing lore..."):
            if run_ai_update(log_input):
                st.success("Lore update complete!")
                time.sleep(1) 
                st.rerun()
            else:
                st.error("Update failed. Check error messages above.")

# --- Render Selected Page (No Changes) ---
if page == "Character Sheet":
    render_character_sheet()
elif page == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()