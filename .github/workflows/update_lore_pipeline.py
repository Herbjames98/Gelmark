# Save this entire file as: update_lore_pipeline_gemini.py

import os
import json
import time
import pprint
import ast
from datetime import datetime

# --- IMPORTANT LIBRARIES TO INSTALL ---
# pip install google-generativeai gitpython
try:
    import google.generativeai as genai
    from git import Repo
except ImportError:
    print("Required libraries not found. Please run: pip install google-generativeai gitpython")
    exit()


# --- ⚙️ Configuration ---
# Get your key from Google AI Studio: https://aistudio.google.com/
GEMINI_API_KEY = "AIzaSyCGN72PxIS0v4Z4zOHgvSwwXdrDhBR3rXM" # <--- PASTE YOUR KEY HERE

# The local file path to your Git repository (your project folder)
REPO_PATH = "." 
LORE_MODULES_DIR = "lore_modules"
JOB_QUEUE_FILE = "job_queue.json"


# --- 🛠️ Helper Functions (Do Not Change) ---

def get_file_content(module_name):
    """Reads the content of a specific lore module file."""
    file_path = os.path.join(REPO_PATH, LORE_MODULES_DIR, f"{module_name}.py")
    with open(file_path, 'r') as f:
        return f.read()

def generate_updated_lore_with_gemini(module_name, current_code, prompt):
    """Sends a request to the Gemini API to update the lore code."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    full_prompt = (
        "You are an expert Python assistant. Your task is to modify a Python dictionary that contains game lore. "
        "I will provide you with the current Python code and a request for a change. "
        "Your response MUST be ONLY the complete, updated Python code for the dictionary variable. "
        "Do not include any other text, explanations, or markdown code fences like ```python."
        "\n\n--- CURRENT CODE ---\n"
        f"{current_code}"
        "\n\n--- CHANGE REQUEST ---\n"
        f"Apply this change: '{prompt}'"
    )
    print("🤖 Sending request to Gemini...")
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ An error occurred with the Gemini API: {e}")
        return None

def save_and_commit(repo, module_name, new_code_string, commit_message):
    """Validates, saves, and pushes the new code to the GitHub repository."""
    try:
        variable_name = new_code_string.split('=', 1).strip()
        dict_string = new_code_string.split('=', 1).strip()
        parsed_dict = ast.literal_eval(dict_string)
    except (ValueError, SyntaxError, IndexError) as e:
        print(f"❌ Validation Error: The code from Gemini is not a valid Python dictionary. Aborting. Error: {e}")
        print("\n--- Received Code ---\n" + new_code_string)
        return False

    formatted_code = f"{variable_name} = {pprint.pformat(parsed_dict, indent=4)}"
    file_path = os.path.join(REPO_PATH, LORE_MODULES_DIR, f"{module_name}.py")
    with open(file_path, 'w') as f:
        f.write(formatted_code)
    print(f"✅ Code validated and saved to {file_path}")

    try:
        print("🌍 Committing and pushing to GitHub...")
        repo.git.add(file_path)
        repo.git.add(JOB_QUEUE_FILE) 
        repo.index.commit(f"Automated lore update for {module_name}: {commit_message}")
        origin = repo.remote(name='origin')
        origin.push()
        print("✅ Successfully pushed to GitHub!")
        return True
    except Exception as e:
        print(f"❌ A Git error occurred: {e}")
        return False

# --- Main Execution Logic ---

def process_job_queue(repo):
    """
    This is the core function with the fix. It checks for jobs and processes them.
    """
    print("Checking for new lore update jobs...")
    
    try:
        with open(JOB_QUEUE_FILE, 'r+') as f:
            # THIS IS THE FIX: Handle the case where the file is empty
            try:
                queue = json.load(f)
            except json.JSONDecodeError:
                queue = [] # If file is empty, treat it as an empty list

            pending_jobs = [job for job in queue if job.get('status') == 'pending']

            if not pending_jobs:
                print("No pending jobs found.")
                return

            job_to_process = pending_jobs
            print(f"Found job {job_to_process['id']} for module '{job_to_process['module']}'")
            
            # Mark job as 'processing' so we don't run it again
            for job in queue:
                if job['id'] == job_to_process['id']:
                    job['status'] = 'processing'
            f.seek(0)
            json.dump(queue, f, indent=4)
            f.truncate()
    except FileNotFoundError:
        print(f"ERROR: Job queue file '{JOB_QUEUE_FILE}' not found. Please create it with '[]' inside.")
        return
    except Exception as e:
        print(f"An unhandled error occurred reading the queue: {e}")
        return

    # --- Execute the job ---
    target_module = job_to_process['module']
    user_prompt = job_to_process['prompt']
    
    current_code = get_file_content(target_module)
    new_code = generate_updated_lore_with_gemini(target_module, current_code, user_prompt)

    success = False
    if new_code:
        success = save_and_commit(repo, target_module, new_code, user_prompt)

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
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        repo = Repo(REPO_PATH)
    except Exception as e:
        print(f"Failed to initialize script: {e}")
        exit()

    process_job_queue(repo)