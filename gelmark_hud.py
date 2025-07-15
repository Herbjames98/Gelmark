# This is the final, complete gelmark_hud.py file.
# It correctly displays all lore AND triggers the bot via repository dispatch.

import streamlit as st
import importlib.util
import os
import json
import requests # Used to send the signal to GitHub
import docx

# === 📁 Helper Function to Load Lore Modules ===
def load_lore_module(module_name):
    """Loads a Python file from the lore_modules directory."""
    try:
        path = os.path.join("my_gm", "lore_modules", f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name, path)
        lore_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lore_module)
        return lore_module
    except Exception as e:
        # Don't show a big error on the page, just return None.
        # The main display logic will handle the missing module.
        print(f"Failed to load module: {module_name} - {e}")
        return None

# === ⚙️ Page Setup ===
st.set_page_config(page_title="Gelmark Lore HUD", layout="wide")
st.title("📖 Gelmark Interactive Lore HUD")


# === 🖊️ Sidebar Editor UI ===
st.sidebar.title("🛠️ Lore Editor")
st.sidebar.subheader("Narrative Save")
uploaded_file = st.sidebar.file_uploader("Upload Conversation Log", type=['txt', 'md', 'docx'])

if st.sidebar.button("Process and Save Narrative"):
    if uploaded_file is None:
        st.sidebar.warning("Please upload a file.")
    else:
        # --- Read the uploaded document ---
        narrative_log = ""
        try:
            if uploaded_file.name.endswith('.docx'):
                document = docx.Document(uploaded_file)
                narrative_log = "\n".join([para.text for para in document.paragraphs])
            else:
                narrative_log = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")
            st.stop()
            
        if not narrative_log:
            st.sidebar.error("Could not extract any text from the file.")
            st.stop()

        # --- Trigger the GitHub Action ---
        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {st.secrets.github.token}"
            }
            url = f"https://api.github.com/repos/{st.secrets.github.repo}/dispatches"
            data = {
                "event_type": "update-lore",
                "client_payload": { "narrative_log": narrative_log }
            }
            
            with st.spinner("Sending update signal to the Lore Bot..."):
                response = requests.post(url, headers=headers, data=json.dumps(data))
                if response.status_code == 204:
                    st.sidebar.success("✅ Success! Lore Bot has been activated.")
                    st.balloons()
                else:
                    st.sidebar.error(f"Error activating bot: {response.status_code} - {response.text}")
        except Exception as e:
            st.sidebar.error("An error occurred while contacting GitHub.")
            st.exception(e)

# === 📖 Main Page Lore Display (Restored) ===
st.sidebar.markdown("---") # Visual separator
pages = { "Prologue": "prologue", "Act 1": "act1", "Act 2": "act2" }
selected_page = st.sidebar.radio("View Lore Section:", list(pages.keys()))

module_key = pages[selected_page]
lore_data = load_lore_module(module_key)

if lore_data:
    section = getattr(lore_data, f"{module_key}_lore", None)
    if section:
        st.subheader(f"📘 {selected_page} Summary")
        st.markdown(section.get("summary", "No summary provided."))

        if "key_events" in section:
            st.subheader("🧩 Key Events")
            st.markdown("\n".join([f"- {event}" for event in section["key_events"]]))

        if "shrines" in section:
            st.subheader("🛕 Shrines")
            for shrine in section["shrines"]:
                st.markdown(f"**Shrine {shrine.get('id', 'N/A')}: {shrine.get('name', 'Unnamed')}**")
                st.markdown(f"- Unlocks: {', '.join(shrine.get('unlocks', []))}")
                st.markdown(f"- Traits: {', '.join(shrine.get('traits', []))}")

        if "visions" in section:
            st.subheader("🔮 Visions")
            st.markdown("\n".join([f"- {v}" for v in section["visions"]]))
            
        if "companions" in section:
            st.subheader("🧑‍🤝‍🧑 Companions")
            for c in section["companions"]:
                if isinstance(c, dict):
                    st.markdown(f"**{c.get('name', 'Unnamed')}** — {c.get('origin', 'Unknown origin')}")
                    st.markdown(f"- Bond: {c.get('bond', 'N/A')}")
                    st.markdown(f"- Sync: {c.get('sync', 'N/A')}")
                    st.markdown(f"- Traits: {', '.join(c.get('trait_alignment', []))}")
                else:
                    st.markdown(f"- {str(c)}")
        
        if "codex_expansions" in section:
            st.subheader("📖 Codex Expansions")
            st.markdown("\n".join([f"- {c}" for c in section["codex_expansions"]]))
    else:
        st.warning(f"Variable '{module_key}_lore' not found in the lore module.")
else:
    st.error(f"Lore module '{module_key}.py' could not be read. Please check the 'my_gm/lore_modules' folder.")