# This is the final, self-contained, local-only Streamlit application.
# It uses the correct, updated Gemini model name.

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

    prompt = f"""You are a master storyteller and game lore keeper. Your task is to update the game's lore files based on a new narrative log.
NARRATIVE LOG: <log>{narrative_log}</log>
CURRENT LORE FILES: <lore>{lore_string}</lore>
INSTRUCTIONS: Your response MUST be a single, valid JSON object where keys are the filenames to be changed and values are the COMPLETE, new content of those files as a single string. Return ONLY the raw JSON object."""

    try:
        # --- THIS IS THE ONLY LINE THAT CHANGED ---
        model = genai.GenerativeModel('gemini-1.0-pro') # Using the correct, stable model name
        
        print("Calling Gemini API with the correct model...")
        response = model.generate_content(prompt)
        response_text = response.text.strip().removeprefix("```json").removesuffix("```")
        updated_files = json.loads(response_text)
        print("Successfully received and parsed AI response.")
    except Exception as e:
        st.error(f"Error calling Gemini or parsing response: {e}")
        return False
        
    st.info("AI processing complete. Writing changes to local files...")
    for filename, content in updated_files.items():
        if filename in current_lore:
            filepath = os.path.join(LORE_FOLDER, filename)
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Successfully wrote changes to {filepath}")
            except Exception as e:
                st.error(f"Error writing to file {filename}: {e}")
                return False
    return True

# --- Main App Interface ---
st.title("📖 Gelmark Local Lore Editor")

st.sidebar.title("🛠️ Lore Updater")
uploaded_file = st.sidebar.file_uploader("Upload Narrative Log", type=['txt', 'md', 'docx'])

if st.sidebar.button("Process and Update Lore"):
    if not os.getenv("GEMINI_API_KEY"):
        st.sidebar.error("GEMINI_API_KEY is not set! Please set the environment variable and restart.")
    elif uploaded_file is None:
        st.sidebar.warning("Please upload a file.")
    else:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        narrative_log = ""
        try:
            if uploaded_file.name.endswith('.docx'):
                narrative_log = "\n".join([p.text for p in docx.Document(uploaded_file).paragraphs])
            else:
                narrative_log = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")
        
        if narrative_log:
            with st.spinner("The AI is rewriting the lore... This may take a moment."):
                success = run_lore_update(narrative_log)
            
            if success:
                st.success("Lore files updated successfully! The page will now reload.")
                st.balloons()
                st.experimental_rerun() 
            else:
                st.error("The lore update failed. Check the console for details.")

# Display Area for the Lore
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
    st.warning(f"Could not display lore for '{selected_page}'. Check the file in '{LORE_FOLDER}'.")