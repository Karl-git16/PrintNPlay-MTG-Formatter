import os
import scrython
import re
import Levenshtein
import unicodedata   # NEW

def _strip_diacritics(s: str) -> str:
    # NFKD splits base + combining marks; drop the marks
    return "".join(ch for ch in unicodedata.normalize("NFKD", s)
                   if unicodedata.category(ch) != "Mn")

def _normalize_filename(s: str) -> str:
    # unify apostrophes, strip them, strip diacritics, collapse spaces, remove forbidden chars
    s = s.replace("’", "'")
    s = s.replace("'", "")
    s = _strip_diacritics(s)
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r'[\\/:"*?<>|]', "_", s)   # Windows-forbidden chars
    return s

def sanitize_filename(name, ScryName):
    if name == "Card Back":
        return name

    card = scrython.cards.Named(fuzzy=name)
    layout = card.layout()

    # Choose the correct face for double-faced/modal cards
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

    # Final, consistent normalization (this is the key change)
    return _normalize_filename(ScryName)

def rename_files(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return

    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if not os.path.isfile(full_path):
            continue

        name, ext = os.path.splitext(filename)
        # remove (…) or […] suffixes and unify quotes early (helps fuzzy search)
        base = name.split('(')[0].split('[')[0].strip().replace("’", "'")
        if base == "Card Back":
            print(f"Skipping 'Card Back': {filename}")
            continue

        try:
            result = scrython.cards.Named(fuzzy=base)
            official_name = sanitize_filename(base, result.name())
        except Exception as e:
            print(f"Could not find match for: {base}")
            continue

        new_name = official_name + ext
        new_path = os.path.join(folder_path, new_name)

        if new_name != filename:
            if os.path.exists(new_path):
                print(f"Skipped (name exists): {new_name}")
                continue
            os.rename(full_path, new_path)
            print(f"Renamed: {filename} to {new_name}")
        else:
            print(f"No change needed for: {filename}")

    print("Done.")
