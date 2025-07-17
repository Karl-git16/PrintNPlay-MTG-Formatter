import os
import shutil


def move_files(source_folder, destination_folder, name_list_file):

    # Read names from the text file (no extensions)
    with open(name_list_file, 'r', encoding='utf-8') as f:
        valid_names = set(line.strip() for line in f if line.strip())

    # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    for filename in os.listdir(source_folder):
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg") or filename.lower().endswith(".png"):
            base_name = os.path.splitext(filename)[0]  # Remove .jpg
            if base_name in valid_names:
                src_path = os.path.join(source_folder, filename)
                dest_path = os.path.join(destination_folder, filename)
                shutil.move(src_path, dest_path)
                print(f"Moved: {filename}")
