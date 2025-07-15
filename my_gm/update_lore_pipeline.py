# This is the final bot script. It reads the narrative log from an environment variable.

import os
import json
from datetime import datetime
import google.generativeai as genai

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NARRATIVE_LOG = os.getenv("NARRATIVE_LOG") # Get log from the workflow
LORE_MODULES_DIR = "lore_modules"

def get_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}"); return ""

def get_all_lore_files_content():
    all_lore = {}
    for filename in os.listdir(LORE_MODULES_DIR):
        if filename.endswith('.py') and '__init__' not in filename:
            filepath = os.path.join(LORE_MODULES_DIR, filename)
            all_lore[filename] = get_file_content(filepath)
    return all_lore

def execute_narrative_save():
    print("Executing narrative save...")
    current_lore_contents = get_all_lore_files_content()
    if not NARRATIVE_LOG:
        print("No narrative log was provided. Aborting."); return False

    lore_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in current_lore_contents.items()])
    prompt = f"""You are a lore keeper for a dark fantasy world. Update the lore files based on the new narrative log.
NARRATIVE LOG: <log>{NARRATIVE_LOG}</log>
CURRENT LORE: <lore>{lore_string}</lore>
INSTRUCTIONS: Your response MUST be a single, valid JSON object where keys are filenames and values are the complete, new file content as a string. Return ONLY the raw JSON object."""

    print("Calling Gemini API...")
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        response_text = response.text.strip().removeprefix("```json").removesuffix("```")
        updated_files = json.loads(response_text)
        print("Successfully received and parsed AI response.")
    except Exception as e:
        print(f"❌ ERROR calling Gemini or parsing response: {e}"); return False

    if not isinstance(updated_files, dict):
        print("AI response was not a dictionary."); return False
    
    for filename, new_content in updated_files.items():
        if filename not in current_lore_contents: continue
        with open(os.path.join(LORE_MODULES_DIR, filename), 'w', encoding='utf-8') as f: f.write(new_content)
        print(f"📝 Wrote content to {filename}")
        
    return True

if __name__ == "__main__":
    if not GEMINI_API_KEY: print("FATAL: GEMINI_API_KEY not set."); exit(1)
    genai.configure(api_key=GEMINI_API_KEY)
    execute_narrative_save()
    print("Bot script finished.")