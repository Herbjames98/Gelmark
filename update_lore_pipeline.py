import os
import openai
from git import Repo
import ast
import pprint

# --- ⚙️ Configuration ---
# It is highly recommended to set this as an environment variable for security
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY" 

# The local file path to your Git repository (your project folder)
# Use "." if the script is in the root of the repository.
REPO_PATH = "." 
LORE_MODULES_DIR = "lore_modules"

# --- 🤖 OpenAI and Git Setup ---
try:
    openai.api_key = OPENAI_API_KEY
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

def generate_updated_lore(module_name, current_code, prompt):
    """
    Sends a request to the OpenAI API to update the lore code.
    """
    system_prompt = (
        "You are an expert Python assistant. Your task is to modify a Python dictionary containing game lore. "
        "The user will provide the current code and a request for a change. "
        "Your response MUST be ONLY the complete, updated Python code for the dictionary variable. "
        "Do not include any other text, explanations, markdown formatting, or the word 'python'."
    )
    
    full_prompt = (
        f"Here is the current Python code for the '{module_name}' module:\n\n"
        f"```python\n{current_code}\n```\n\n"
        f"Please apply this change: '{prompt}'"
    )

    print("🤖 Sending request to OpenAI... This may take a moment.")
    try:
        response = openai.chat.completions.create(
            model="gpt-4",  # Using a more advanced model is better for code generation
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ An error occurred with the OpenAI API: {e}")
        return None

def save_and_commit(module_name, new_code_string, commit_message):
    """
    Validates, saves, and pushes the new code to the GitHub repository.
    """
    # 1. Validate the code is a valid Python dictionary
    try:
        # ast.literal_eval is a safe way to parse Python literals
        parsed_dict = ast.literal_eval(new_code_string.split('=', 1)[1].strip())
        variable_name = new_code_string.split('=', 1)[0].strip()
    except (ValueError, SyntaxError) as e:
        print(f"❌ Validation Error: The code from OpenAI is not a valid Python dictionary. Aborting. Error: {e}")
        print("\n--- Received Code ---\n")
        print(new_code_string)
        return

    # 2. Format and Save the code
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
    new_code = generate_updated_lore(target_module, current_code, user_prompt)

    if new_code:
        save_and_commit(target_module, new_code, user_prompt)