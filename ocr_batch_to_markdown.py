import os
import pytesseract
from PIL import Image
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ==== Configuration ====
# The path is now correct based on your screenshot, assuming your username is hrbrt
# If your username is different, update the path!
INPUT_FOLDER = r"C:\Users\hrbrt\OneDrive\Pictures\COE2_Skills"
OUTPUT_FILE = "Skill_Codex.md" # This will be saved in the same folder you run the script from
LANG = "eng"

# ==== Markdown Setup ====
# Updated function to include the class name from the folder structure
def format_skill_entry(image_file):
    class_name = image_file.parent.name.replace("Class_", "") # "Class_Brawler" -> "Brawler"
    skill_name = image_file.stem # Gets the filename without extension
    
    # Process the image with OCR
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img, lang=LANG)
    cleaned = text.strip().replace('\n', ' ').replace('\r', '')
    
    # Return a much more organized Markdown format
    return f"### 🗡️ {class_name}: {skill_name}\n\n" + "```\n" + cleaned + "\n```\n\n"

# ==== Run Script ====
def run_ocr_batch(input_dir, output_file):
    input_path = Path(input_dir)
    output_path = Path(output_file)
    all_entries = []

    if not input_path.exists():
        print(f"[ERROR] Folder '{input_path}' does not exist.")
        return

    # Use rglob() to search recursively into sub-folders
    image_files = sorted(input_path.rglob("*.*"))
    
    if not image_files:
        print(f"[WARNING] No image files found in '{input_path}' or its subdirectories.")
        return

    print(f"Found {len(image_files)} images to process...")

    for image_file in image_files:
        # Skips non-image files
        if image_file.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            continue
        try:
            print(f"Processing {image_file.relative_to(input_path)}...")
            entry = format_skill_entry(image_file)
            all_entries.append(entry)
        except Exception as e:
            print(f"[ERROR] Failed to process {image_file.name}: {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 🧠 Skill Codex Export\n\n")
        f.writelines(all_entries)

    print(f"✅ Done. Output saved to: {output_path.resolve()}")

# Run immediately
run_ocr_batch(INPUT_FOLDER, OUTPUT_FILE)