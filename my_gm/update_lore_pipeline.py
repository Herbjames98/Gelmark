# This is the final, simplified pipeline script that does not use GitPython.

import os
import json
from datetime import datetime
import google.generativeai as genai

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LORE_MODULES_DIR = "lore_modules"
JOB_QUEUE_FILE = "job_queue.json"

# --- Helper Functions ---

def get_file_content(filepath):
    """Reads the content of a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

def get_all_lore_files_content():
    """Reads all lore files."""
    all_lore = {}
    lore_path = os.path.join(os.getcwd(), LORE_MODULES_DIR)
    if not os.path.exists(lore_path):
        print(f"ERROR: Lore modules directory not found at {lore_path}")
        return {}
    for filename in os.listdir(lore_path):
        if filename.endswith('.py') and '__init__' not in filename:
            filepath = os.path.join(lore_path, filename)
            all_lore[filename] = get_file_content(filepath)
    return all_lore

def validate_code_changes(filename, new_code_str):
    """Checks if the new code is valid Python."""
    try:
        compile(new_code_str, filename, 'exec')
        print(f"✅ Validation passed for {filename}.")
        return True
    except SyntaxError as e:
        print(f"❌ VALIDATION FAILED for {filename}: {e}")
        return False

# --- Core AI Function ---

def execute_narrative_save(job):
    """Calls Gemini AI and updates lore files."""
    print(f"Executing narrative save for job {job['id']}...")
    narrative_log = job['data']
    current_lore_contents = get_all_lore_files_content()
    if not current_lore_contents:
        print("Could not read any lore files. Aborting.")
        return False

    lore_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in current_lore_contents.items()])
    prompt = f"""
    You are a master storyteller and game lore keeper for a dark fantasy world. Your task is to update the game's lore files based on a new narrative log.
    NARRATIVE LOG: <log>{narrative_log}</log>
    CURRENT LORE FILES: <lore>{lore_string}</lore>
    INSTRUCTIONS:
    1. Read the new log and integrate its events into the existing lore files.
    2. Your entire response MUST be a single, valid JSON object.
    3. The keys of the JSON object are the filenames to be changed (e.g., "prologue.py").
    4. The values are the COMPLETE, new content of those files as a single string.
    5. Ensure the Python code within each file remains syntactically correct.
    Return ONLY the raw JSON object.
    """

    print("Calling Gemini API...")
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        response_text = response.text.strip().removeprefix("```json").removesuffix("```")
        updated_files = json.loads(response_text)
        print("Successfully received and parsed AI response.")
    except Exception as e:
        print(f"❌ ERROR: Failed to call Gemini AI or parse response: {e}")
        return False

    if not isinstance(updated_files, dict):
        print("AI response was not a dictionary. Aborting.")
        return False

    for filename, new_content in updated_files.items():
        if filename not in current_lore_contents:
            print(f"⚠️ Skipping new file '{filename}'.")
            continue
        if validate_code_changes(filename, new_content):
            filepath = os.path.join(LORE_MODULES_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"📝 Wrote content to {filepath}")
        else:
            print(f"🛑 Aborting save due to validation failure in {filename}.")
            return False
    return True

# --- Main Execution Loop ---

def process_job_queue():
    """Checks for jobs and processes them."""
    print("Bot script starting...")
    try:
        with open(JOB_QUEUE_FILE, 'r+') as f:
            queue = json.load(f)
            pending_jobs = [j for j in queue if j.get('status') == 'pending']
            if not pending_jobs:
                print("No pending jobs found.")
                return

            job = pending_jobs[0]
            success = execute_narrative_save(job)

            for item in queue:
                if item['id'] == job['id']:
                    item['status'] = 'completed' if success else 'failed'
            f.seek(0)
            json.dump(queue, f, indent=4)
            f.truncate()
            print(f"Job {job['id']} marked as {'completed' if success else 'failed'}.")
    except FileNotFoundError:
        print(f"'{JOB_QUEUE_FILE}' not found. No jobs to process.")
    except Exception as e:
        print(f"An unhandled error occurred in process_job_queue: {e}")

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("FATAL ERROR: GEMINI_API_KEY environment variable not set.")
        exit(1)
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    process_job_queue()
    print("Bot script finished.")
