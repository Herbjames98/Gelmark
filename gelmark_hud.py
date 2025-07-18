# This is the final, fully-functional version of the local application.
# It correctly handles filenames from the AI and removes the auto-rerun for clarity.

import streamlit as st
import os
import json
import google.generativeai as genai
import docx
import importlib.util

# --- Configuration and Setup ---
st.set_page_config(page_title="Gelmark Lore HUD", layout="wide")
LORE_FOLDER = os.path.join("my_gm", "lore_modules")

# --- Core Functions ---

def load_lore_module(module_name):
    """Loads a Python file from the lore_modules directory."""
    try:
        path = os.path.join(LORE_FOLDER, f"{module_name}.py")
        if not os.path.exists(path): return None
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        st.error(f"Error loading {module_name}: {e}")
        return None

def get_all_lore_content():
    """Reads all current lore files into a dictionary."""
    all_lore = {}
    for filename in os.listdir(LORE_FOLDER):
        if filename.endswith('.py') and '__init__' not in filename:
            filepath = os.path.join(LORE_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                all_lore[filename] = f.read()
    return all_lore

def run_lore_update(narrative_log):
    """The main AI logic function."""
    st.info("Preparing lore and contacting the Gemini AI...")
    
    current_lore = get_all_lore_content()
    lore_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in current_lore.items()])

    prompt = f"""You are a master storyteller. Your task is to update the game's lore files based on a new narrative log.
NARRATIVE LOG: <log>{narrative_log}</log>
CURRENT LORE FILES: <lore>{lore_string}</lore>
INSTRUCTIONS: Your response MUST be a single, valid JSON object. Keys must be the FILENAMES (e.g., "act1.py") and values must be the COMPLETE, new file content as a single string. Return ONLY the raw JSON object."""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        updated_files = json.loads(response.text.strip().removeprefix("```json").removesuffix("```"))
    except Exception as e:
        st.error(f"An error occurred while processing the AI response: {e}")
        st.subheader("Raw AI Response:")
        st.code(response.text if 'response' in locals() else "No response from AI.", language="text")
        return False

    st.subheader("Parsed AI Response:")
    st.json(updated_files)

    if not updated_files:
        st.warning("The AI returned an empty response. No files were changed.")
        return False
        
    st.info("AI processing complete. Writing changes to local files...")
    files_written = 0
    for key, content in updated_files.items():
        # --- THIS IS THE FIX ---
        # Get just the filename from the key (e.g., 'lore_modules/act1.py' -> 'act1.py')
        filename = os.path.basename(key) 
        
        if filename in current_lore:
            filepath = os.path.join(LORE_FOLDER, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            st.write(f"✅ Successfully wrote changes to `{filename}`.")
            files_written += 1
        else:
            st.write(f"⚠️ Skipping unknown file from AI: `{filename}`.")
    
    # Check if any work was actually done
    if files_written == 0:
        st.warning("AI response processed, but no matching files were found to update.")
        return False

    return True

# --- Main App Interface ---
st.title("📖 Gelmark Local Lore Editor")
st.sidebar.title("🛠️ Lore Updater")
st.sidebar.subheader("Paste Narrative Log")
narrative_log_input = st.sidebar.text_area("Paste your new story information here:", height=300)

if st.sidebar.button("Process and Update Lore"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("GEMINI_API_KEY is not set!")
    elif not narrative_log_input:
        st.sidebar.warning("Please paste a narrative log.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        with st.spinner("The AI is rewriting the lore..."):
            success = run_lore_update(narrative_log_input)
        
        if success:
            st.success("Lore files updated successfully! Refresh the page (F5) to see the new content.")
            st.balloons()
            # The st.rerun() line is now permanently removed for clarity.
        else:
            st.error("The lore update failed. See details above.")

# --- Display Area ---
st.sidebar.markdown("---")
pages = {"Prologue": "prologue", "Act 1": "act1", "Act 2": "act2"}
selected_page = st.sidebar.radio("View Lore Section:", list(pages.keys()))
module_data = load_lore_module(pages[selected_page])

if module_data:
    section = getattr(module_data, f"{pages[selected_page]}_lore", {})
    st.subheader(f"📘 {selected_page} Summary")
    st.markdown(section.get("summary", "No summary found."))
    if "key_events" in section:
        st.subheader("🧩 Key Events")
        st.markdown("\n".join([f"- {event}" for event in section["key_events"]]))
    if "companions" in section:
        st.subheader("🧑‍🤝‍🧑 Companions")
        for c in section["companions"]:
            if isinstance(c, dict):
                st.markdown(f"**{c.get('name', 'Unnamed')}** — {c.get('origin', 'Unknown')}")
            else:
                st.markdown(f"- {str(c)}")
else:
    st.warning(f"Could not display lore for '{selected_page}'.")