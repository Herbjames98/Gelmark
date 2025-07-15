# DIAGNOSTIC SCRIPT - This will make a visible change.

import os
import json
from datetime import datetime

LORE_MODULES_DIR = "lore_modules"
JOB_QUEUE_FILE = "job_queue.json"
TEST_FILE_TO_MODIFY = os.path.join(LORE_MODULES_DIR, "prologue.py")

def make_test_change():
    """Reads a file, adds a timestamp, and writes it back."""
    print(f"Attempting to modify the file: {TEST_FILE_TO_MODIFY}")

    # Read the existing content
    try:
        with open(TEST_FILE_TO_MODIFY, 'r') as f:
            original_content = f.read()
    except Exception as e:
        print(f"ERROR: Could not read the test file. {e}")
        return

    # Create the new content
    timestamp = f"# Bot ran and modified this file at: {datetime.now().isoformat()}\n"
    new_content = timestamp + original_content

    # Write the new content back to the file
    try:
        with open(TEST_FILE_TO_MODIFY, 'w') as f:
            f.write(new_content)
        print("SUCCESS: Wrote new content to the test file.")
    except Exception as e:
        print(f"ERROR: Could not write to the test file. {e}")


def process_job_queue():
    """Checks for jobs and processes them."""
    print("Checking for new lore update jobs...")
    
    try:
        with open(JOB_QUEUE_FILE, 'r+') as f:
            try:
                queue = json.load(f)
            except json.JSONDecodeError:
                queue = []

            pending_jobs = [job for job in queue if job.get('status') == 'pending']
            if not pending_jobs:
                print("No pending jobs found. Nothing to do.")
                return

            print(f"Found {len(pending_jobs)} pending job(s). Processing one.")
            job_to_process = pending_jobs[0]
            
            # --- RUN THE TEST ---
            make_test_change()

            # Mark job as completed
            for job in queue:
                if job['id'] == job_to_process['id']:
                    job['status'] = 'completed'
                    job['finished_at'] = datetime.now().isoformat()
            
            # Update the queue file
            f.seek(0)
            json.dump(queue, f, indent=4)
            f.truncate()
            print(f"Job {job_to_process['id']} marked as completed.")

    except FileNotFoundError:
        print(f"'{JOB_QUEUE_FILE}' not found. No jobs to process.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_job_queue()