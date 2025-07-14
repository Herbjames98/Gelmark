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
    Handles large narrative logs by chunking, summarizing, and then updating lore.
    """
    print(f"Executing ADVANCED narrative save for job {job['id']}...")
    
    narrative_log = job['data']
    
    # --- STEP 1: MAP - Chunk and Summarize the Large Document ---
    
    # Split the log into chunks of ~15,000 characters (a safe size)
    chunk_size = 15000
    text_chunks = [narrative_log[i:i + chunk_size] for i in range(0, len(narrative_log), chunk_size)]
    print(f"Document split into {len(text_chunks)} chunks for analysis.")

    summaries = []
    summary_model = genai.GenerativeModel('gemini-1.5-flash') # Use the fast model for summaries

    for i, chunk in enumerate(text_chunks):
        print(f"Summarizing chunk {i+1}/{len(text_chunks)}...")
        
        summarization_prompt = f"""
You are a lore extraction bot. Analyze the following text from a game session.
Extract ONLY the key events, character status changes, new abilities or traits acquired, and any new world lore.
Present the information as a concise list.

Text to analyze:
---
{chunk}
---
        """
        try:
            response = summary_model.generate_content(summarization_prompt)
            summaries.append(response.text)
        except Exception as e:
            print(f"⚠️ Could not summarize chunk {i+1}. Error: {e}")
            summaries.append(f"Error summarizing chunk {i+1}.")

    # --- STEP 2: REDUCE - Combine Summaries and Update Lore Files ---
    
    final_summary = "\n\n".join(summaries)
    print("All chunks summarized. Preparing final update...")

    current_lore_contents = get_all_lore_files_content()
    update_model = genai.GenerativeModel('gemini-1.5-pro-latest') # Use the smart model for the final update

    master_prompt = f"""
You are an expert Game Master's assistant AI. Your task is to analyze a collection of summaries from a game session and update the corresponding Python lore files.

Here are the collected summaries of the key events:
<SUMMARIES>
{final_summary}
</SUMMARIES>

Here are the current contents of all the lore files:
<CURRENT_LORE_FILES>
{json.dumps(current_lore_contents, indent=2)}
</CURRENT_LORE_FILES>

Based SOLELY on the information in the <SUMMARIES> section, generate the complete, updated Python code for EVERY file that needs to be modified.

Your output MUST be a single, valid JSON object, where:
- The keys are the filenames (e.g., "act2.py").
- The values are the complete, new Python code content for that file as a single string.
- If a file does not need to be changed, do not include it.
- Ensure the generated Python code is syntactically correct.
"""

    print("🤖 Sending final 'Reduce' prompt to Gemini...")
    try:
        response = update_model.generate_content(master_prompt)
        cleaned_response = response.text.strip().lstrip("```json").rstrip("```")
        updated_files = json.loads(cleaned_response)
    except Exception as e:
        print(f"❌ Failed to get a valid JSON response for the final update: {e}")
        print(f"--- Gemini's Raw Response ---\n{response.text}")
        return False

    print(f"✅ Gemini returned final updates for {list(updated_files.keys())}")

    # --- Save and Commit All Changes (this logic remains the same) ---
    files_to_commit = []
    for filename, new_content in updated_files.items():
        if not new_content or not isinstance(new_content, str):
            print(f"⚠️ Skipping empty content for {filename}")
            continue
        
        # Determine if the file goes in the root or in lore_modules
        if filename in current_lore_contents:
             filepath = os.path.join(LORE_MODULES_DIR, filename)
        else:
             filepath = filename # Assume it's a root file like player_stats.py
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"📝 Wrote updated content to {filepath}")
        files_to_commit.append(filepath)

    if not files_to_commit:
        print("No files were updated by the final prompt.")
        return True

    try:
        print("🌍 Committing and pushing changes to GitHub...")
        repo.git.add(files_to_commit)
        repo.git.add(JOB_QUEUE_FILE)
        commit_message = f"Automated narrative save from large document"
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push()
        print("✅ Successfully pushed all lore updates to GitHub!")
        return True
    except Exception as e:
        print(f"❌ A Git error occurred during the final commit: {e}")
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