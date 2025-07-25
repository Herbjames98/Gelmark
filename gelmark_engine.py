import streamlit as st
import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
import importlib.util
import ast  # --- ADDED: The robust library for code modification

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
        # Invalidate cache to ensure we get the latest version after an update
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


# --- AI Integration (MODIFIED SECTION) ---
def apply_patches_with_ast(updated_files_patches):
    """
    Intelligently patches Python files using AST, which understands code structure.
    This is the robust replacement for the old regex method.
    """
    for fname, patches in updated_files_patches.items():
        dst = os.path.join(SCRIPT_DIR, fname) if fname == "player_state.py" else os.path.join(LORE_FOLDER, fname)

        # Read existing file or prepare to create a new one
        source_code = ""
        if os.path.exists(dst):
            with open(dst, "r", encoding="utf-8") as f:
                source_code = f.read()

        try:
            # Parse the source code into a tree structure
            tree = ast.parse(source_code)
            applied_patches = {var: False for var in patches}

            class Patcher(ast.NodeTransformer):
                def visit_Assign(self, node):
                    # Handle single assignments like 'variable = ...'
                    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                        var_name = node.targets[0].id
                        if var_name in patches:
                            try:
                                # The AI gives a string of a dict/list, so we parse it into a code node
                                new_value_str = patches[var_name]
                                new_value_node = ast.parse(new_value_str, mode='eval').body
                                node.value = new_value_node
                                applied_patches[var_name] = True
                            except Exception as e:
                                st.warning(f"AST Patcher: Could not apply patch for '{var_name}' in `{fname}`. Malformed AI response? Error: {e}")
                    return node

            # Apply the transformation
            new_tree = Patcher().visit(tree)

            # For any patch not applied (because the variable didn't exist), append it to the file.
            for var_name, applied in applied_patches.items():
                if not applied:
                    new_assignment_str = f"\n{patches[var_name]}"
                    new_assign_node = ast.parse(f"{var_name} = {new_assignment_str}").body[0]
                    new_tree.body.append(new_assign_node)

            # Convert the modified tree back to clean, formatted code
            new_code = ast.unparse(new_tree)

            with open(dst, "w", encoding="utf-8") as f:
                f.write(new_code)
            st.success(f"✅ Securely patched `{fname}`.")

        except Exception as e:
            st.error(f"❌ Critical error patching `{fname}` with AST: {e}")
            return False
    return True

def run_ai_update(narrative_log):
    st.info("🧠 Processing with Gemini 1.5 Pro...")
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

    # This prompt is the same, asking for specific patches
    prompt = f"""
You are a meticulous Gemini AI historian maintaining structured Python game files.
Based on the <narrative_log>, generate the necessary code changes for the <game_files>.

<narrative_log>{narrative_log}</narrative_log>
<past_memories>{past_memories}</past_memories>
<game_files>{''.join([f'--- {fn} ---\n{content}\n\n' for fn, content in file_snapshots.items()])}</game_files>

Your job:
1. Update traits, companions, inventory, or events.
2. Merge "Grace" and "G.R.A.C.E." into a single logical entry.
3. Respond with a JSON object containing ONLY the Python variables that need changing. The value in the JSON must be a string containing a valid Python dict or list.

    Perfect response format:
    ```json
    {{
      "player_state.py": {{
        "companions": "[{{'name': 'The Valking Captain', 'description': 'A formidable but now loyal ally.'}}]",
        "traits": "{{'active_traits': ['Rebirth'], 'echoform_traits': [], 'hybrid_fusion_traits': []}}"
      }},
      "act3.py": {{
        "act3_lore": "{{'summary': 'A new act begins.', 'major_events': []}}"
      }}
    }}
    ```
4. After the JSON block, give a short (2-3 line) memory summary of the update.
Respond only in the raw JSON block + memory summary. No other text.
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        full_text = response.text.strip()
        
        json_str = full_text
        summary_text = ""
        
        # Robustly find the JSON block and the summary
        if "```json" in full_text:
            match = re.search(r"```json\s*([\s\S]+?)\s*```", full_text)
            if match:
                json_str = match.group(1)
                summary_text = full_text[match.end():].strip()
        elif "}}" in full_text:
            # Fallback for when the markdown block is missing
            split_point = full_text.rfind("}}") + 2
            json_str = full_text[:split_point]
            summary_text = full_text[split_point:].strip()

        updated_files_patches = json.loads(json_str)

    except Exception as e:
        st.error(f"Gemini response parsing failed: {e}")
        st.code(response.text if 'response' in locals() else "No response from AI.")
        return False

    # Call the new, safe patching function
    if not apply_patches_with_ast(updated_files_patches):
        return False

    # Save new memory summary
    if summary_text:
        memory_log.append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M'),
            "summary": summary_text
        })
        save_memory_log(memory_log)

    return True
# --- END OF MODIFIED SECTION ---

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
                        if k not in ['name', 'description']:
                            st.markdown(f"**{k.replace('_',' ').title()}:** {v}")
            else:
                st.markdown(f"- {item}")
    elif isinstance(data, dict):
        for k, v in data.items():
            st.markdown(f"**{k.replace('_',' ').title()}:** {v}")

# --- Pages ---
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

# --- Main UI ---
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
                time.sleep(1) # Give a moment for user to see success message
                st.rerun()
            else:
                st.error("Update failed. Check error messages above.")

# --- Render Selected Page ---
if page == "Character Sheet":
    render_character_sheet()
elif page == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()