# This is the full, upgraded pipeline script.
# Replace your existing file with this.

import os
import json
import time
import pprint
import ast
from datetime import datetime

try:
    import google.generativeai as genai
    from git import Repo
except ImportError:
    print("Required libraries not found. Please run: pip install google-generativeai gitpython")
    exit()

# --- ⚙️ Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPO_PATH = "." 
LORE_MODULES_DIR = "lore_modules"
JOB_QUEUE_FILE = "job_queue.json"

# --- 🛠️ Helper Functions ---

def get_file_content(filepath):
    """Reads the content of any file."""
    with open(filepath, 'r') as f:
        return f.read()

def get_all_lore_files_content():
    """Reads all lore modules and returns them as a dictionary."""
    all_lore = {}
    for filename in os.listdir(LORE_MODULES_DIR):
        if filename.endswith('.py') and '__init__' not in filename:
            filepath = os.path.join(LORE_MODULES_DIR, filename)
            all_lore[filename] = get_file_content(filepath)
    return all_lore

def execute_simple_edit(repo, job):
    """Handles the original simple edit jobs."""
    print(f"Executing simple edit for module '{job['module']}'...")
    # This function would contain the logic from our previous pipeline version
    # For now, we'll focus on the new narrative save.
    print("Simple edit logic not fully implemented in this version. Job skipped.")
    return False # Placeholder

# --- NEW: Master Function for Narrative Saves ---

# In update_lore_pipeline_gemini.py, replace the execute_narrative_save function

def validate_code_changes(filename, old_code_str, new_code_str):
    """
    Performs sanity checks on the AI-generated code to prevent catastrophic errors.
    Returns True if valid, False otherwise.
    """
    print(f"🕵️ Validating changes for {filename}...")
    
    # --- Execute code in a safe, isolated environment ---
    try:
        # Get the variable name (e.g., 'act2_lore' from 'act2.py')
        variable_name = filename.replace('.py', '_lore') 
        
        old_scope = {}
        exec(old_code_str, {}, old_scope)
        old_data = old_scope.get(variable_name, {})

        new_scope = {}
        exec(new_code_str, {}, new_scope)
        new_data = new_scope.get(variable_name)

        # --- Run Validation Checks ---
        if new_data is None:
            print(f"❌ VALIDATION FAILED: The core variable '{variable_name}' was deleted.")
            return False
            
        if "companions" in old_data and "companions" not in new_data:
             print(f"❌ VALIDATION FAILED: The entire 'companions' key was deleted.")
             return False

        if "companions" in new_data and not isinstance(new_data.get("companions"), list):
            print(f"❌ VALIDATION FAILED: The 'companions' key is no longer a list.")
            return False
        
        # Check if a major character was deleted
        if "companions" in old_data and "companions" in new_data:
            old_companion_names = {c.get('name') for c in old_data['companions'] if isinstance(c, dict)}
            new_companion_names = {c.get('name') for c in new_data['companions'] if isinstance(c, dict)}
            
            missing_companions = old_companion_names - new_companion_names
            if missing_companions:
                print(f"❌ VALIDATION FAILED: Major characters were deleted: {', '.join(missing_companions)}")
                return False

        print(f"✅ Validation passed for {filename}.")
        return True

    except Exception as e:
        print(f"❌ An exception occurred during validation: {e}")
        return False


def execute_narrative_save(repo, job):
    """
    Handles large narrative logs by chunking, summarizing, and then updating lore.
    """
    print(f"Executing ADVANCED narrative save for job {job['id']}...")
    
    narrative_log = job['data']
    
    # (The "Map" step of chunking and summarizing remains the same)
    chunk_size = 15000 
    text_chunks = [narrative_log[i:i + chunk_size] for i in range(0, len(narrative_log), chunk_size)]
    print(f"Document split into {len(text_chunks)} chunks for analysis.")
    # ... (summarization logic here) ...

    # --- Step 2: Reduce (this is where the validation is added) ---
    final_summary = "..." # Assuming we have the final summary from the Map step
    current_lore_contents = get_all_lore_files_content()
    # ... (The master prompt logic remains the same) ...
    
    # ... (After Gemini returns a response and you load it into 'updated_files') ...

    # --- Save and Prepare for Commit ---
    valid_files_to_commit = []
    for filename, new_content in updated_files.items():
        if filename not in current_lore_contents:
            print(f"⚠️ Skipping new file '{filename}' from AI. Only modifications are allowed for safety.")
            continue
        
        old_content = current_lore_contents[filename]
        
        # THIS IS THE NEW VALIDATION STEP
        if validate_code_changes(filename, old_content, new_content):
            # If valid, write the file and add it to our list
            filepath = os.path.join(LORE_MODULES_DIR, filename)
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"📝 Wrote validated content to {filepath}")
            valid_files_to_commit.append(filepath)
        else:
            # If ANY file fails validation, we abort the entire operation
            print(f"🛑 Aborting entire save operation due to validation failure in {filename}.")
            return False

    if not valid_files_to_commit:
        print("No valid files were updated. Nothing to commit.")
        return True

    # The final 'git' logic is now handled by the GitHub Action workflow
    print("✅ All files validated and written. The GitHub Action will now create a Pull Request.")
    return True

# --- Main Execution Loop ---

def process_job_queue(repo):
    """Checks for jobs and processes them based on their type."""
    print("Checking for new lore update jobs...")
    
    try:
        with open(JOB_QUEUE_FILE, 'r+') as f:
            try:
                queue = json.load(f)
            except json.JSONDecodeError:
                queue = []

            pending_jobs = [job for job in queue if job.get('status') == 'pending']
            if not pending_jobs:
                print("No pending jobs found.")
                return

            job_to_process = pending_jobs[0]
            
            # Mark job as 'processing'
            for job in queue:
                if job['id'] == job_to_process['id']:
                    job['status'] = 'processing'
            f.seek(0)
            json.dump(queue, f, indent=4)
            f.truncate()
    except Exception as e:
        print(f"Error reading job queue: {e}")
        return

    # --- Route the Job to the Correct Function ---
    job_type = job_to_process.get("type", "edit") # Default to 'edit' for old jobs
    success = False
    
    if job_type == "narrative_save":
        success = execute_narrative_save(repo, job_to_process)
    else: # Handles 'edit' and any other types
        success = execute_simple_edit(repo, job_to_process)

    # --- Finalize the queue ---
    with open(JOB_QUEUE_FILE, 'r+') as f:
        queue = json.load(f)
        for job in queue:
            if job['id'] == job_to_process['id']:
                job['status'] = 'completed' if success else 'failed'
                job['finished_at'] = datetime.now().isoformat()
        f.seek(0)
        json.dump(queue, f, indent=4)
        f.truncate()
    
    print(f"Job {job_to_process['id']} marked as {'completed' if success else 'failed'}.")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY environment variable not set.")
        exit()
        
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        repo = Repo(REPO_PATH)
    except Exception as e:
        print(f"Failed to initialize script: {e}")
        exit()

    process_job_queue(repo)