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

def _summarize_changes(before, after):
    changes = {"stats": {}, "gold": 0, "items_add": [], "items_remove": [], "traits_add": [], "traits_remove": [], "relationships": {}, "level_up": None}
    # Stats
    b = (before.get("stats") or {}); a = (after.get("stats") or {})
    for k in set(b) | set(a):
        dv = int(a.get(k,0)) - int(b.get(k,0))
        if dv: changes["stats"][k] = dv
    # Gold
    bg = int(((before.get("inventory") or {}).get("gold") or 0))
    ag = int(((after.get("inventory") or {}).get("gold") or 0))
    changes["gold"] = ag - bg
    # Items
    bki = set(((before.get("inventory") or {}).get("key_items") or []))
    aki = set(((after.get("inventory") or {}).get("key_items") or []))
    changes["items_add"] += sorted(list(aki - bki))
    changes["items_remove"] += sorted(list(bki - aki))
    # Traits (active names only)
    def _names(lst): return [x.get("name", x) if isinstance(x, dict) else str(x) for x in (lst or [])]
    btr = set(_names(((before.get("traits") or {}).get("active_traits"))))
    atr = set(_names(((after.get("traits") or {}).get("active_traits"))))
    changes["traits_add"] += sorted(list(atr - btr))
    changes["traits_remove"] += sorted(list(btr - atr))
    # Relationships
    br = (before.get("relationships") or {}); ar = (after.get("relationships") or {})
    for k in set(br) | set(ar):
        dv = int(ar.get(k,0)) - int(br.get(k,0))
        if dv: changes["relationships"][k] = dv
    # Level up flag
    bl = (before.get("flags") or {}).get("level_title")
    al = (after.get("flags") or {}).get("level_title")
    if bl != al and al:
        changes["level_up"] = al
    return changes

def _render_change_toast(ch):
    bits = []
    if ch.get("level_up"):
        st.success(f"🔶 Level Up: **{ch['level_up']}**")
    if ch["stats"]:
        stat_str = ", ".join([f"{k} {('+' if v>0 else '')}{v}" for k,v in ch["stats"].items()])
        bits.append(f"📊 {stat_str}")
    if ch["gold"]:
        bits.append(f"🪙 Gold {('+' if ch['gold']>0 else '')}{ch['gold']}")
    if ch["items_add"]:
        bits.append("🔑 +" + ", ".join(ch["items_add"]))
    if ch["traits_add"]:
        bits.append("✨ +" + ", ".join(ch["traits_add"]))
    if ch["relationships"]:
        rel_str = ", ".join([f"{k} {('+' if v>0 else '')}{v}" for k,v in ch["relationships"].items()])
        bits.append(f"🤝 {rel_str}")
    if bits:
        st.info(" • ".join(bits))

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
    # Load live state
    from save_io import load_state
    state_defaults = load_module_from_file(PLAYER_STATE_FILE)
    live = load_state(state_defaults)

    # Profile header pulls from defaults if present
    display_section("🧍 Profile", getattr(state_defaults, "player_profile", {}))

    # --- Level & Stats ---
    st.subheader("📈 Stats & Level")
    stats = live.get("stats", {}) or getattr(state_defaults, "stats_overview", {})
    # Remove summary key from stats display (do this before try/except)
    if isinstance(stats, dict) and 'Total Stat Points' in stats:
        stats = {k: v for k, v in stats.items() if k != 'Total Stat Points'}

    # compute level info if mechanics available
    try:
        from mechanics import compute_level
        lvl = compute_level(stats)
        cols = st.columns([2,1,1])
        with cols[0]:
            st.metric("Title", live.get("flags", {}).get("level_title", lvl.get("title", "Novice of the Gel")))
        with cols[1]:
            st.metric("Total Stat Points", lvl.get("total", sum(stats.values())))
        with cols[2]:
            nxt = lvl.get("next_cap")
            if nxt:
                need = max(0, nxt - lvl.get("total", 0))
                st.metric("To Next Tier", need)
            else:
                st.metric("To Next Tier", "—")
        # simple progress bar to next tier
        if lvl.get("next_cap") is not None:
            rng = max(1, lvl["next_cap"] - lvl["current_floor"])
            prog = min(1.0, max(0.0, (lvl["total"] - lvl["current_floor"]) / rng))
            st.progress(prog)
    except Exception:
        st.caption("Level data unavailable (mechanics module not loaded).")

    # Show stats grid
    cols = st.columns(3)
    for i, (k, v) in enumerate(stats.items()):
        cols[i % 3].metric(label=k, value=v)

    # --- Traits ---
    traits = live.get("traits", {}) or getattr(state_defaults, "traits", {})
    display_section("✨ Active Traits", traits.get("active_traits"))
    display_section("🔮 Echoform Traits", traits.get("echoform_traits"))
    display_section("🧬 Hybrid/Fusion Traits", traits.get("hybrid_fusion_traits"))

    # --- Inventory (compact equipment grid) ---
    inv = live.get("inventory", {}) or getattr(state_defaults, "inventory", {})
    st.subheader("🎒 Inventory")
    st.markdown(f"**Gold:** {inv.get('gold', 0)}")
    # Equipment grid
    eq = inv.get("equipment", {}) or {}
    ecols = st.columns(2)
    with ecols[0]:
        st.markdown("**⚔️ Weapon**")
        st.write(eq.get("weapon") or "—")
        st.markdown("**🛡️ Armor**")
        st.write(eq.get("armor") or "—")
        st.markdown("**🌀 Offhand**")
        st.write(eq.get("offhand") or "—")
    with ecols[1]:
        st.markdown("**💍 Accessory 1**")
        st.write(eq.get("accessory_1") or "—")
        st.markdown("**💍 Accessory 2**")
        st.write(eq.get("accessory_2") or "—")

    display_section("🔑 Key Items", inv.get("key_items"))
    display_section("📿 Artifacts & Relics", inv.get("artifacts_relics"))

    # --- Social / System ---
    st.subheader("🤝 Relationships")
    rel = live.get("relationships", {})
    if rel:
        rcols = st.columns(3)
        for i, (k,v) in enumerate(sorted(rel.items())):
            rcols[i % 3].metric(k, v)
    else:
        st.caption("No relationships tracked yet.")

    st.subheader("⚙️ Flags")
    flags = live.get("flags", {})
    if flags:
        for k,v in sorted(flags.items()):
            st.markdown(f"**{k}:** {v}")
    else:
        st.caption("No flags set yet.")


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
    from save_io import load_state, save_state, reset_state
    from story_flow import SCENES
    from mechanics import apply_effects
    import uuid, time, datetime

    # ---------- UI polish: CSS overlay & fade ----------
    st.markdown(
        """
        <style>
        .gm-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,.65);
            display: none; align-items: center; justify-content: center;
            z-index: 9999; animation: gmFade .25s ease-in forwards;
        }
        .gm-overlay.show { display: flex; }
        @keyframes gmFade { from { opacity: 0 } to { opacity: 1 } }
        .gm-card {
            background: rgba(20,20,20,.85); padding: 18px 22px; border-radius: 14px;
            font-size: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "gm_transition" not in st.session_state:
        st.session_state["gm_transition"] = False
    if "gm_pending_choice" not in st.session_state:
        st.session_state["gm_pending_choice"] = None

    # Display overlay if transitioning
    if st.session_state.get("gm_transition"):
        st.markdown('<div class="gm-overlay show"><div class="gm-card">Generating next scene…</div></div>', unsafe_allow_html=True)

    # ---------- Load defaults ----------
    state_mod = load_module_from_file(PLAYER_STATE_FILE)
    if not state_mod:
        st.error("Could not load defaults from player_state.py.")
        return
    live = load_state(state_mod)
    # Backfill lore modules if they're empty so the browser isn't blank
    try:
        from lore_update import backfill_lore_if_empty
        backfill_lore_if_empty(live)
    except Exception:
        pass

    # ---------- Sidebar controls ----------
    st.sidebar.subheader("🧠 Story Mode")

    use_ai = st.sidebar.toggle("Use AI-Generated Scenes", value=True)
    force_ai = st.sidebar.toggle("Force AI after every choice", value=True)
    hard_reset = st.sidebar.checkbox("Also wipe AI lore & memory (hard reset)", value=False)
    if st.sidebar.button("🧹 Reset Save (Start at Prologue)"):
        st.session_state["gm_transition"] = True
        st.session_state["gm_pending_choice"] = {"reset": True, "hard": hard_reset}
        st.rerun()

    # ---------- Handle pending choice / reset BEFORE rendering scene ----------
    if st.session_state.get("gm_pending_choice"):
        pending = st.session_state["gm_pending_choice"]
        # reset requested
        if pending.get("reset"):
            hard = bool(pending.get("hard"))
            live = reset_state(state_mod, hard=hard)
            save_state(live)
            st.session_state["gm_pending_choice"] = None
            st.session_state["gm_transition"] = False
            st.rerun()
        else:
            # Process a stored choice
            choice = pending["choice"]
            scene_snapshot = pending["scene_snapshot"]
            before = json.loads(json.dumps(live))
            apply_effects(live, choice.get("effects", {}))

            # Act gating
            flags = live.get("flags", {}) if isinstance(live.get("flags", {}), dict) else live.setdefault("flags", {})
            if flags.get("prologue_done") and live["position"].get("act",0) == 0:
                live["position"]["act"] = 1

            # Save history
            snap = {
                "prev_scene_id": scene_snapshot["id"],
                "prev_title": scene_snapshot.get("title",""),
                "prev_text": scene_snapshot.get("text",""),
                "choice_label": choice.get("label",""),
                "effects": choice.get("effects", {}),
                "timestamp": time.time()
            }
            live.setdefault("scene_history", []).append(snap)

            # Generate scene FIRST; only advance if success
            ok = False
            if use_ai:
                try:
                    lore_snaps = {}
                    if os.path.exists(LORE_FOLDER):
                        for fname in os.listdir(LORE_FOLDER):
                            if fname.endswith(".py") and "__init__" not in fname:
                                mod = load_module_from_file(os.path.join(LORE_FOLDER, fname))
                                if mod:
                                    key = fname[:-3]
                                    lore = getattr(mod, f"{key}_lore", {})
                                    lore_snaps[key] = str(lore.get("summary",""))
                    mem = load_memory_log()
                    tail = "\n".join(f"[{m['timestamp']}] {m['summary']}" for m in mem[-5:])
                    from ai_story import generate_scene
                    prev = snap
                    gen_scene = generate_scene(live, lore_snaps, tail, prev=prev)
                    # Cache & advance
                    live.setdefault("scene_cache", {})[gen_scene["id"]] = gen_scene
                    live["position"]["scene"] = gen_scene["id"]
                    # Append to story_log
                    entry = {
                        "scene_id": scene_snapshot["id"],
                        "title": scene_snapshot.get("title",""),
                        "text": scene_snapshot.get("text",""),
                        "choice": choice.get("label",""),
                        "effects": choice.get("effects", {}),
                        "result_scene_id": gen_scene["id"],
                        "timestamp": time.time(),
                        "timestamp_human": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    live.setdefault("story_log", []).append(entry)
                    try:
                        from lore_update import update_lore_from_scene
                        update_lore_from_scene(scene_snapshot, choice, gen_scene)
                    except Exception:
                        pass
                    ok = True
                except Exception as e:
                    st.warning(f"AI scene generation failed: {e}. Staying on current scene.")

            if not ok:
                # If AI failed, stay put and do NOT change scene
                pass
            save_state(live)
            # Optional: change summary toast if available
            if "gm_last_changes" in st.session_state and st.session_state["gm_last_changes"]:
                pass  # left in place if helpers exist
            st.session_state["gm_pending_choice"] = None
            st.session_state["gm_transition"] = False
            st.rerun()

    # ---------- Render current scene ----------
    pos = live.get("position", {})
    scene_id = pos.get("scene", "prologue_start")

    from story_flow import SCENES
    merged = dict(SCENES); merged.update(live.get("scene_cache", {}))

    # Ensure current scene exists; generate if missing (but don't reset to prologue)
    if scene_id not in merged and use_ai:
        try:
            lore_snaps = {}
            if os.path.exists(LORE_FOLDER):
                for fname in os.listdir(LORE_FOLDER):
                    if fname.endswith(".py") and "__init__" not in fname:
                        mod = load_module_from_file(os.path.join(LORE_FOLDER, fname))
                        if mod:
                            key = fname[:-3]
                            lore = getattr(mod, f"{key}_lore", {})
                            lore_snaps[key] = str(lore.get("summary",""))
            mem = load_memory_log()
            tail = "\n".join(f"[{m['timestamp']}] {m['summary']}" for m in mem[-5:])
            from ai_story import generate_scene
            prev = (live.get("scene_history") or [])[-1] if live.get("scene_history") else None
            gen_scene = generate_scene(live, lore_snaps, tail, prev=prev)
            live.setdefault("scene_cache", {})[gen_scene["id"]] = gen_scene
            scene_id = gen_scene["id"]
            live["position"]["scene"] = scene_id
            save_state(live)
        except Exception as e:
            st.warning(f"AI scene build failed: {e}. Showing last valid scene.")

    scene = merged.get(scene_id) or SCENES.get("prologue_start")
    if not scene:
        st.error("No valid scene found.")
        return

    st.header(scene.get("title", scene_id).replace("_", " "))
    st.write(scene.get("text", ""))

    # Render choice buttons
    for choice in scene.get("choices", []):
        btn_key = f"choice_{scene_id}_{choice.get('id','x')}"
        if st.button(choice.get("label","Continue"), key=btn_key):
            st.session_state["gm_transition"] = True
            st.session_state["gm_pending_choice"] = {"choice": choice, "scene_snapshot": {"id": scene_id, "title": scene.get("title",""), "text": scene.get("text","")}}
            st.rerun()

    # Narrative Log viewer + export
    st.subheader("🧾 Narrative Log")
    log = live.get("story_log", [])
    if log:
        for entry in log[-10:]:
            st.markdown(f"**{entry.get('timestamp_human','')} — {entry.get('title','')}**")
            st.markdown(entry.get('text',''))
            st.markdown(f"_You chose:_ **{entry.get('choice','')}**")
            st.markdown("---")
        if st.button("📄 Export Full Narrative Log (.txt)"):
            out_path = os.path.join(os.path.dirname(__file__), "narrative_log.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                for e in log:
                    f.write(
                        f"{e.get('timestamp_human', '')}\n"
                        f"{e.get('title', '')}\n"
                        f"{e.get('text', '')}\n"
                        f"CHOICE: {e.get('choice', '')}\n"
                        "---\n"
                    )
            st.success(f"Saved to {out_path}")
    else:
        st.caption("Narrative log is empty.")


# --- Main UI ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Character Sheet", "Lore Browser", "Play the Game"])

if page == "Character Sheet":
    render_character_sheet()
elif page == "Lore Browser":
    render_lore_browser()
else:
    render_play_game_page()