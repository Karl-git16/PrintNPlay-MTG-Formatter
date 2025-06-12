import os

def rename_files(folder_path):
    """
    Renames files by removing parentheses/brackets and apostrophes from names.
    """
    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return

    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)

        if os.path.isfile(full_path):
            name, ext = os.path.splitext(filename)

            # Remove text in () or []
            name = name.split('(')[0].strip()
            name = name.split('[')[0].strip()

            # Remove both straight and curly apostrophes
            for char in ["'", "’"]:
                name = name.replace(char, "")

            new_name = name + ext
            new_path = os.path.join(folder_path, new_name)

            if new_name != filename:
                if os.path.exists(new_path):
                    print(f"⚠️ Skipped (name exists): {new_name}")
                    continue
                os.rename(full_path, new_path)
                print(f"Renamed: {filename} → {new_name}")
            else:
                print(f"No change needed for: {filename}")

    print("Done.")
