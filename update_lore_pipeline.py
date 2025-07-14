import os
import google.generativeai as genai
from git import Repo
import ast
import pprint
import json
import time

# --- ⚙️ Configuration (remains the same) ---
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" 
REPO_PATH = "." 
LORE_MODULES_DIR = "lore_modules"
JOB_QUEUE_FILE = "job_queue.json"

# --- 🤖 API and Git Setup (remains the same) ---
# ... (all functions like get_file_content, generate_updated_lore_with_gemini, etc. remain the same) ...
# I will include them here for completeness.

def get_file_content(module_name):
    file_path = os.path.join(REPO_PATH, LORE_MODULES_DIR, f"{module_name}.py")
    with open(file_path, 'r') as f:
        return f.read()

def generate_updated_lore_with_gemini(module_name, current_code, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    full_prompt = (
        "You are an expert Python assistant... (Your full prompt here)"
    )
    print("🤖 Sending request to Gemini...")
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ An error occurred with the Gemini API: {e}")
        return None

def save_and_commit(module_name, new_code_string, commit_message):
    try:
        # Code validation
        parsed_dict = ast.literal_eval(new_code_string.split('=', 1)[1].strip())
        variable_name = new_code_string.split('=', 1)[0].strip()
        
        # Format and save
        formatted_code = f"{variable_name} = {pprint.pformat(parsed_dict, indent=4)}"
        file_path = os.path.join(REPO_PATH, LORE_MODULES_DIR, f"{module_name}.py")
        with open(file_path, 'w') as f:
            f.write(formatted_code)
        print(f"✅ Code validated and saved to {file_path}")

        # Commit and push
        repo = Repo(REPO_PATH)
        repo.git.add(file_path)
        # Also add the job queue file to save its updated state
        repo.git.add(JOB_QUEUE_FILE) 
        repo.index.commit(f"Automated lore update for {module_name}: {commit_message}")
        origin = repo.remote(name='origin')
        origin.push()
        print("✅ Successfully pushed to GitHub!")
        return True
    except Exception as e:
        print(f"❌ An error occurred during save/commit: {e}")
        return False


# --- Main Execution Logic (This is what changes) ---
def process_job_queue():
    print("Checking for new lore update jobs...")
    
    # Safely read and lock the queue
import sys
import datetime

with open(JOB_QUEUE_FILE, 'r+') as f:
        queue = json.load(f)
        pending_jobs = [job for job in queue if job.get('status') == 'pending']

        if not pending_jobs:
            print("No pending jobs found.")
            return

        # Get the oldest pending job
        job_to_process = pending_jobs[0]
        print(f"Found job {job_to_process['id']} for module '{job_to_process['module']}'")
        
        # Mark job as "processing" to prevent re-running
        for job in queue:
            if job['id'] == job_to_process['id']:
                job['status'] = 'processing'
                break
        f.seek(0)
        json.dump(queue, f, indent=4)
        f.truncate()

    # --- Execute the job ---
    target_module = job_to_process['module']
    user_prompt = job_to_process['prompt']
    
    current_code = get_file_content(target_module)
    new_code = generate_updated_lore_with_gemini(target_module, current_code, user_prompt)

    success = False
    if new_code:
        success = save_and_commit(target_module, new_code, user_prompt)

    # --- Finalize the queue ---
    with open(JOB_QUEUE_FILE, 'r+') as f:
        queue = json.load(f)
        for job in queue:
            if job['id'] == job_to_process['id']:
                job['status'] = 'completed' if success else 'failed'
                job['finished_at'] = datetime.now().isoformat()
                break
        f.seek(0)
        json.dump(queue, f, indent=4)
        f.truncate()
    
    print(f"Job {job_to_process['id']} marked as {'completed' if success else 'failed'}.")


    if __name__ == "__main__":
    # Configure API and Repo
      genai.configure(api_key=GEMINI_API_KEY)
    
    # This script now runs once to process one job.
    # For continuous running, you would wrap this in a loop with a sleep timer.
    process_job_queue()