# This is the final app. It sends a repository_dispatch event.

import streamlit as st
import os
import json
import requests # Used to send the signal to GitHub
import docx

st.set_page_config(page_title="Gelmark Lore HUD", layout="wide")
st.title("📖 Gelmark Lore HUD")

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
            # Get the GitHub token and repo name from Streamlit secrets
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {st.secrets.github.token}"
            }
            url = f"https://api.github.com/repos/{st.secrets.github.repo}/dispatches"
            data = {
                "event_type": "update-lore",
                "client_payload": {
                    "narrative_log": narrative_log
                }
            }
            
            with st.spinner("Sending update signal to the Lore Bot..."):
                response = requests.post(url, headers=headers, data=json.dumps(data))
                
                if response.status_code == 204:
                    st.sidebar.success("✅ Success! Lore Bot has been activated.")
                    st.balloons()
                else:
                    st.sidebar.error(f"Error activating bot: {response.status_code} - {response.text}")

        except Exception as e:
            st.sidebar.error(f"An error occurred while contacting GitHub.")
            st.exception(e)