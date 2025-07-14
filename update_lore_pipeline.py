import os
import google.generativeai as genai
from git import Repo
import ast
import pprint

# --- ⚙️ Configuration ---
# Get your key from Google AI Studio: https://aistudio.google.com/
# It is highly recommended to set this as an environment variable for security
GEMINI_API_KEY = "AIzaSyAQ5hOepF_TWqJpptBKuiym0sjKr0o1pGA"

# The local file path to your Git repository (your project folder)
# Use "." if the script is in the root of the repository.
REPO_PATH = "." 
LORE_MODULES_DIR = "lore_modules"

# --- 🤖 Google Gemini and Git Setup ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    repo = Repo(REPO_PATH)
except Exception as e:
    print(f"Error initializing script: {e}")
    exit()

def get_lore_files():
    """Finds all available lore modules."""
    path = os.path.join(REPO_PATH, LORE_MODULES_DIR)
    return [f.replace('.py', '') for f in os.listdir(path) if f.endswith('.py') and f != '__init__.py']

def get_file_content(module_name):
    """Reads the content of a specific lore module file."""
    file_path = os.path.join(REPO_PATH, LORE_MODULES_DIR, f"{module_name}.py")
    with open(file_path, 'r') as f:
        return f.read()

def generate_updated_lore_with_gemini(module_name, current_code, prompt):
    """
    Sends a request to the Gemini API to update the lore code.
    """
    # Using a newer, fast model. You can also use 'gemini-1.5-pro' for higher quality.
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Gemini works well with a single, detailed prompt.
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

    print("🤖 Sending request to Gemini... This may take a moment.")
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ An error occurred with the Gemini API: {e}")
        return None

def save_and_commit(module_name, new_code_string, commit_message):
    """
    Validates, saves, and pushes the new code to the GitHub repository.
    """
    # 1. Validate the code is a valid Python dictionary
    try:
        # ast.literal_eval is a safe way to parse Python literals
        parsed_dict = ast.literal_eval(new_code_string.split('=', 1).strip())
        variable_name = new_code_string.split('=', 1).strip()
    except (ValueError, SyntaxError) as e:
        print(f"❌ Validation Error: The code from Gemini is not a valid Python dictionary. Aborting. Error: {e}")
        print("\n--- Received Code ---\n")
        print(new_code_string)
        return

    # 2. Format and Save the code using pprint for nice formatting
    formatted_code = f"{variable_name} = {pprint.pformat(parsed_dict, indent=4)}"
    file_path = os.path.join(REPO_PATH, LORE_MODULES_DIR, f"{module_name}.py")
    with open(file_path, 'w') as f:
        f.write(formatted_code)
    print(f"✅ Code validated and saved to {file_path}")

    # 3. Commit and Push using Git
    try:
        print("🌍 Committing and pushing to GitHub...")
        repo.git.add(file_path)
        repo.index.commit(f"Automated lore update for {module_name}: {commit_message}")
        origin = repo.remote(name='origin')
        origin.push()
        print("✅ Successfully pushed to GitHub! Your Streamlit app will now redeploy.")
    except Exception as e:
        print(f"❌ A Git error occurred: {e}")

# --- Main Execution Logic ---
if __name__ == "__main__":
    lore_files = get_lore_files()
    if not lore_files:
        print("No lore files found in the 'lore_modules' directory.")
        exit()

    print("Available Lore Modules:", ", ".join(lore_files))
    target_module = input("Which lore module do you want to edit? ")

    if target_module not in lore_files:
        print("Invalid module name.")
        exit()

    user_prompt = input(f"What change would you like to make to '{target_module}'? ")

    current_code = get_file_content(target_module)
    new_code = generate_updated_lore_with_gemini(target_module, current_code, user_prompt)

    if new_code:
        save_and_commit(target_module, new_code, user_prompt)