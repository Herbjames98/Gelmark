# This is the final, fully-functional pipeline script.
# It has been simplified to remove the unused GitPython library.

import os
import json
from datetime import datetime
import google.generativeai as genai

# --- ⚙️ Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LORE_MODULES_DIR = "lore_modules"
JOB_QUEUE_FILE = "job_queue.json"

# --- 🛠️ Helper Functions ---

def get_file_content(filepath):
    """Reads the content of any file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

def get_all_lore_files_content():
    """Reads all lore modules and returns them as a dictionary."""
    all_lore = {}
    for filename in os.listdir(LORE_MODULES_DIR):
        if filename.endswith('.py') and '__init__' not in filename:
            filepath = os.path.join(LORE_MODULES_DIR, filename)
            all_lore[filename] = get_file_content(filepath)
    return all_lore

def validate_code_changes(filename, new_code_str):
    """A simple validation to ensure the new code is still valid Python."""
    try:
        compile(new_code_str, filename, 'exec')
        print(f"✅ Validation passed for {filename}.")
        return True
    except SyntaxError as e:
        print(f"❌ VALIDATION FAILED for {filename}: Invalid Python syntax. {e}")
        return False

# --- Main Narrative Save Function ---

def execute_narrative_save(job):
    """
    Handles narrative logs by calling the Gemini AI and updating lore files.
    """
    print(f"Executing narrative save for job {job['id']}...")
    
    narrative_log = job['data']
    current_lore_contents = get_all_lore_files_content()

    # --- Prepare the AI Prompt ---
    lore_string = "\n\n".join([f"--- File: {name} ---\n{content}" for name, content in current_lore_contents.items()])
    
    prompt = f"""
    You are a master storyteller and game lore keeper for a dark fantasy world named Gelmark.
    Your task is to update the game's lore files based on a new narrative log.
    
    NARRATIVE LOG TO PROCESS:
    <narrative_log>
    {narrative_log}
    </narrative_log>

    CURRENT LORE FILES:
    <current_lore>
    {lore_string}
    </current_lore>

    INSTRUCTIONS:
    1. Read the new log and integrate its events into the existing lore files.
    2. Your response MUST be a single, valid JSON object.
    3. The keys of the JSON object are the filenames to be changed (e.g., "prologue.py").
    4. The values are the COMPLETE, new content of those files, as a single string.
    5. Ensure the Python code within each file remains syntactically correct.
    
    Return ONLY the raw JSON object.
    """

    # --- Call the Gemini API ---
    print("Calling Gemini API...")
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        response_text = response.text.strip().removeprefix("```json").removesuffix("```")
        updated_files = json.loads(response_text)
        print("Successfully received and parsed AI response.")

    except Exception as e:
        print(f"❌ ERROR: Failed to call Gemini AI or parse its response: {e}")
        return False

    # --- Validate and Write Files ---
    if not isinstance(updated_files, dict):
        print("AI response was not a dictionary of files. Aborting.")
        return False

    for filename, new_content in updated_files.items():
        if filename not in current_lore_contents:
            print(f"⚠️ Skipping new file '{filename}' from AI.")
            continue
        
        if validate_code_changes(filename, new_content):
            filepath = os.path.join(LORE_MODULES_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"📝 Wrote validated content to {filepath}")
        else:
            print(f"🛑 Aborting save due to validation failure in {filename}.")
            return False

    print("✅ All files validated and written.")
    return True

# --- Main Execution Loop ---

def process_job_queue():
    """Checks for jobs and processes them."""
    print("Checking for new lore update jobs...")
    
    try:
        with open(JOB_QUEUE_FILE, 'r+') as f:
            queue = json.load(f)
            pending_jobs = [job for job in queue if job.get('status') == 'pending']
            if not pending_jobs:
                print("No pending jobs found.")
                return

            job_to_process = pending_jobs[0]
            
            success = execute_narrative_save(job_to_process)

            for job in queue:
                if job['id'] == job_to_process['id']:
                    job['status'] = 'completed' if success else 'failed'
            
            f.seek(0)
            json.dump(queue, f, indent=4)
            f.truncate()
            print(f"Job {job_to_process['id']} marked as {'completed' if success else 'failed'}.")

    except FileNotFoundError:
        print(f"'{JOB_QUEUE_FILE}' not found. No jobs to process.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY environment variable not set.")
        exit()
        
    genai.configure(api_key=GEMINI_API_KEY)
    process_job_queue()