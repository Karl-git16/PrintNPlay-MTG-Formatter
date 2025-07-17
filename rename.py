import os
import scrython
import re
import Levenshtein

import re
import Levenshtein

def sanitize_filename(name, ScryName):
    if(name == "Card Back"):
        return name
    card = scrython.cards.Named(fuzzy=name)
    layout = card.layout()
    if "//" in ScryName or "/" in ScryName:
        if layout in ["double_faced", "transform", "modal_dfc"]:
            if "//" in ScryName:
                parts = ScryName.split(" // ")
            elif "/" in ScryName:
                parts = ScryName.split("/")
            dist1 = Levenshtein.distance(name, parts[0])
            dist2 = Levenshtein.distance(name, parts[1])
            ScryName = parts[0] if dist1 <= dist2 else parts[1]
        else:
            ScryName = card.name().split("//")[0].strip().replace("'", "")

    for char in ["'", "’"]:
        ScryName = ScryName.replace(char, "")
    
    ScryName = ScryName.strip()

    # Remove or replace forbidden characters for filenames
    ScryName = re.sub(r'[\\/:"*?<>|]', "_", ScryName)

    return ScryName



def rename_files(folder_path):
    """
    Renames files by matching their names to official Magic: The Gathering card names using Scryfall.
    Cleans up filename first, then queries Scryfall for closest match.
    """
    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        return

    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)

        if os.path.isfile(full_path):
            name, ext = os.path.splitext(filename)

            # Clean initial name by removing (), [], and apostrophes
            name = name.split('(')[0].strip()
            name = name.split('[')[0].strip()
            for char in ["'", "’"]:
                name = name.replace(char, "")
            if name == "Card Back":
                print(f"Skipping 'Card Back': {filename}")
                sanitize_filename(name, name)  # Ensure we still sanitize
                continue
            # Use Scryfall to get correct card name
            try:
                result = scrython.cards.Named(fuzzy=name)
                official_name = sanitize_filename(name, result.name())
            except scrython.exceptions.ScryfallError:
                print(f"⚠️ Could not find match for: {name}")
                continue

            # Rename to official name
            new_name = official_name + ext
            new_path = os.path.join(folder_path, new_name)

            if new_name != filename:
                if os.path.exists(new_path):
                    print(f"⚠️ Skipped (name exists): {new_name}")
                    continue
                os.rename(full_path, new_path)
                print(f"✅ Renamed: {filename} → {new_name}")
            else:
                print(f"No change needed for: {filename}")
            
        
    print("🎉 Done.")

#rename_files("Cards")