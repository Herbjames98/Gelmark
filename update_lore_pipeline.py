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

def execute_narrative_save(repo, job):
    """
    Reads a full narrative log, gets all current lore, and asks Gemini
    to perform a comprehensive update across multiple files.
    """
    print(f"Executing narrative save for job {job['id']}...")
    
    narrative_log = job['data']
    current_lore_contents = get_all_lore_files_content()

    # This is the "Master Prompt" that does the heavy lifting
    master_prompt = f"""
You are an expert Game Master's assistant AI. Your task is to analyze a narrative conversation log from a game session and update the corresponding Python lore files.

Here is the full conversation log of the event that just occurred:
<NARRATIVE_LOG>
{narrative_log}
</NARRATIVE_LOG>

Here are the current contents of the lore files:
<CURRENT_LORE_FILES>
{json.dumps(current_lore_contents, indent=2)}
</CURRENT_LORE_FILES>

Based on the narrative log, your task is to identify ALL necessary changes and generate the complete, updated Python code for EVERY file that needs to be modified.

Your output MUST be a single, valid JSON object, where:
- The keys are the filenames that need to be updated (e.g., "act2.py").
- The values are the complete, new Python code content for that file as a single string.
- If a file does not need to be changed, DO NOT include it in your response.
- The Python code you generate must be syntactically correct.

Example of a valid response:
{{
  "act2.py": "act2_lore = {{\\n    'summary': 'After the hero helped Caelik overcome his echo...',\\n    'companions': [ ... updated Caelik entry ... ],\\n    'codex_expansions': ['Fire Without Mastery', ...],\\n    ...\\n}}",
  "player_stats.py": "player_stats = {{\\n    'traits': ['Flameforward Oath'],\\n    ...\\n}}"
}}

Now, analyze the provided log and files and generate the JSON object with the required file updates.
"""

    print("🤖 Sending master prompt to Gemini...")
    model = genai.GenerativeModel('gemini-1.5-pro-latest') # Use the most powerful model for this complex task
    try:
        response = model.generate_content(master_prompt)
        # Clean the response to ensure it's a valid JSON object
        cleaned_response = response.text.strip().lstrip("```json").rstrip("```")
        updated_files = json.loads(cleaned_response)
    except Exception as e:
        print(f"❌ Failed to get or parse a valid JSON response from Gemini: {e}")
        print(f"--- Gemini's Raw Response ---\n{response.text}")
        return False

    print(f"✅ Gemini returned updates for {list(updated_files.keys())}")

    # --- Save and Commit All Changes ---
    files_to_commit = []
    for filename, new_content in updated_files.items():
        # Basic validation to ensure it's not empty
        if not new_content or not isinstance(new_content, str):
            print(f"⚠️ Skipping empty or invalid content for {filename}")
            continue
        
        filepath = os.path.join(LORE_MODULES_DIR, filename)
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"📝 Wrote updated content to {filepath}")
        files_to_commit.append(filepath)

    if not files_to_commit:
        print("No valid files were updated. Nothing to commit.")
        return True # The job is done, even if nothing changed.

    try:
        print("🌍 Committing and pushing changes to GitHub...")
        repo.git.add(files_to_commit)
        repo.git.add(JOB_QUEUE_FILE) # Also commit the updated job queue
        commit_message = f"Automated narrative save: Caelik's Dual Echo Trial"
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push()
        print("✅ Successfully pushed lore updates to GitHub!")
        return True
    except Exception as e:
        print(f"❌ A Git error occurred: {e}")
        return False

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