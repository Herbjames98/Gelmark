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

    game_files_string = ''.join([f"--- {fn} ---\n{content}\n\n" for fn, content in file_snapshots.items()])

    prompt = (
        "You are a meticulous Gemini AI historian maintaining structured Python game files.\n"
        "Based on the <narrative_log>, generate the necessary code changes for the <game_files>.\n\n"
        f"<narrative_log>{narrative_log}</narrative_log>\n"
        f"<past_memories>{past_memories}</past_memories>\n\n"
        "<game_files>\n" + game_files_string + "</game_files>\n\n"
        "Your job:\n"
        "1. Update traits, companions, inventory, or events.\n"
        "2. Merge \"Grace\" and \"G.R.A.C.E.\" into a single logical entry.\n"
        "3. Respond with a JSON object containing ONLY the Python variables that need changing. The value in the JSON must be a string containing a valid, single-line Python dict or list. Ensure the string uses single quotes for keys and values.\n"
        "4. If a new lore file is needed (e.g., for a new Act), create it.\n\n"
        "Respond only in the raw JSON block + memory summary. No other text or explanations."
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        full_text = response.text.strip()
        
        json_str, summary_text = "", ""
        if "```json" in full_text:
            match = re.search(r"```json\s*([\s\S]+?)\s*```", full_text)
            if match:
                json_str = match.group(1)
                summary_text = full_text[match.end():].strip()
        else:
            json_str = full_text # Assume entire response is JSON if no block is found
        
        updated_files_patches = json.loads(json_str)

    except Exception as e:
        st.error(f"Gemini response parsing failed: {e}")
        st.code(response.text if 'response' in locals() else "No response from AI.")
        return False

    if not apply_patches_with_ast(updated_files_patches):
        return False

    if summary_text:
        memory_log.append({"timestamp": time.strftime('%Y-%m-%d %H:%M'), "summary": summary_text})
        save_memory_log(memory_log)

    return True

# --- Display Utilities ---
def display_section(title, data):
    if not data: return
    st.subheader(title)
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                with st.expander(f"🔹 {item.get('name', 'Unnamed')}"):
                    st.markdown(f"*{item.get('description', '')}*")
                    for k, v in item.items():
                        if k not in ['name', 'description']: st.markdown(f"**{k.replace('_',' ').title()}:** {v}")
            else: st.markdown(f"- {item}")
    elif isinstance(data, dict):
        for k, v in data.items(): st.markdown(f"**{k.replace('_',' ').title()}:** {v}")

# --- Pages ---
def render_character_sheet():
    from save_io import load_state
    st.title("📜 Character Sheet")
    defaults_mod = load_module_from_file(PLAYER_STATE_FILE)
    live = load_state(defaults_mod)
    # ... (rest of character sheet logic remains the same)

def render_lore_browser():
    st.title("📖 Gelmark Lore Browser")
    if not os.path.exists(LORE_FOLDER):
        return st.warning("Missing `lore_modules` folder.")
    def sort_key(n): return 0 if n == 'prologue' else int(n.replace('act', '')) if n.startswith('act') else 999
    lore_files = sorted([f[:-3] for f in os.listdir(LORE_FOLDER) if f.endswith(".py") and "__init__" not in f], key=sort_key)
    # ... (rest of lore browser logic remains the same)

def render_play_game_page():
    st.title("🎲 Play the Game")
    from save_io import load_state, save_state, reset_state
    from story_flow import SCENES
    from mechanics import apply_effects
    from ai_story import generate_scene
    
    defaults_mod = load_module_from_file(PLAYER_STATE_FILE)
    if not defaults_mod:
        st.error("CRITICAL: player_state.py could not be loaded.")
        st.stop()

    live = load_state(defaults_mod)

    # --- Sidebar ---
    st.sidebar.subheader("🧠 Story Mode")
    use_ai = st.sidebar.toggle("Use AI-Generated Scenes", value=True)
    force_ai = st.sidebar.toggle("Force AI after every choice", value=True)
    hard_reset = st.sidebar.checkbox("Also wipe AI lore & memory (hard reset)", value=False)
    if st.sidebar.button("🧹 Reset Save (Start at Prologue)"):
        reset_state(defaults_mod, hard=hard_reset)
        st.rerun()

    # --- Handle Pending Choice ---
    if "pending_choice" in st.session_state:
        pending = st.session_state.pop("pending_choice")
        choice = pending["choice"]
        scene_snapshot = pending["scene_snapshot"]
        
        apply_effects(live, choice.get("effects", {}))
        live["position"]["scene"] = choice.get("to", live["position"]["scene"])
        
        history_snap = { "timestamp": time.time(), "timestamp_human": time.strftime("%Y-%m-%d %H:%M"), **pending }
        live["scene_history"].append(history_snap)
        live["story_log"].append(history_snap)
        
        save_state(live)
        st.rerun()

    # --- Render Current Scene ---
    scene_id = live["position"]["scene"]
    merged_scenes = {**SCENES, **live.get("scene_cache", {})}
    scene = merged_scenes.get(scene_id)
    
    should_force_generate = use_ai and (force_ai or not (scene and scene.get("choices")))
    if should_force_generate:
        try:
            with st.spinner("🧠 Generating next scene..."):
                lore_snaps = {} # ... (lore loading) ...
                mem = load_memory_log()
                tail = "\n".join(f"[{m['timestamp']}] {m['summary']}" for m in mem[-5:])
                prev = (live.get("scene_history") or [None])[-1]
                
                generated_scene = generate_scene(live, lore_snaps, tail, prev=prev)
                
                live["position"]["scene"] = generated_scene["id"]
                live["scene_cache"][generated_scene["id"]] = generated_scene
                save_state(live)
                
                scene = generated_scene
                st.rerun()

        except Exception as e:
            st.error(f"AI scene generation failed: {e}")
            # Add state dump for easier debugging in the future
            with st.expander("Show current state for debugging"):
                st.json(live)
            scene = scene or SCENES.get("prologue_start")

    if not scene:
        st.error("CRITICAL: No valid scene could be found. Resetting.")
        live["position"]["scene"] = "prologue_start"
        save_state(live)
        st.rerun()

    st.header(scene.get("title", "An Unknown Place"))
    st.markdown(scene.get("text", "_The world is quiet here..._"))

    for choice in scene.get("choices", []):
        btn_key = f"choice_{scene.get('id', scene_id)}_{choice.get('id','x')}"
        if st.button(choice.get("label", "Continue..."), key=btn_key):
            st.session_state["pending_choice"] = {
                "choice": choice,
                "scene_snapshot": {"id": scene.get("id"), "title": scene.get("title"), "text": scene.get("text")}
            }
            st.rerun()

    st.subheader("🧾 Narrative Log")
    log = live.get("story_log", [])
    if log:
        for entry in reversed(log[-10:]):
            title = entry.get("scene_snapshot", {}).get("title") or "Untitled Scene"
            with st.expander(f"{entry.get('timestamp_human','')} — {title}"):
                st.markdown(entry.get("scene_snapshot", {}).get("text",''))
                st.markdown(f"> _You chose:_ **{entry.get('choice',{}).get('label','')}**")
    else:
        st.caption("Narrative log is empty.")

# --- Main App Router ---
st.sidebar.title("Navigation")
page_options = ["Play the Game", "Character Sheet", "Lore Browser"]
page = st.sidebar.radio("Go to:", page_options, index=0)

if page == "Play the Game":
    render_play_game_page()
elif page == "Character Sheet":
    render_character_sheet()
elif page == "Lore Browser":
    render_lore_browser()