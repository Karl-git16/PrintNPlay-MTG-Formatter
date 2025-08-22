from PIL import Image, ImageOps
from io import BytesIO
import scrython
import requests
import re
import os
from rename import sanitize_filename
import numpy as np

def modify_and_download_image(image_url, folderName, name_clean):
    if not image_url:
        return

    # Download the image
    response = requests.get(image_url)
    response.raise_for_status()

    # Open image and ensure it's RGBA
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    # Convert to NumPy array and fix transparency (flatten near-transparent to black)
    img_np = np.array(img)
    transparent_mask = img_np[:, :, 3] < 220
    img_np[transparent_mask] = [0, 0, 0, 255]
    img = Image.fromarray(img_np, "RGBA")

    # Flatten onto black background (remove glow)
    img_rgb = Image.new("RGB", img.size, (0, 0, 0))
    img_rgb.paste(img, mask=img.split()[3])

    # Add a single black border
    border_size = 38
    img_with_border = ImageOps.expand(img_rgb, border=border_size, fill='black')

    # Sanitize filename (fall back to 'card' if name is empty/None)
    safe_name = sanitize_filename(name_clean or "card", name_clean or "card")

    # Save to folder as PNG
    os.makedirs(folderName, exist_ok=True)
    save_path = os.path.join(folderName, safe_name + ".png")
    img_with_border.save(save_path)
    print(f"Saved image: {save_path}")

def clean_name(name: str) -> str:
    if not name:
        return ""
    name_clean = re.sub(r"^\d+\s+", "", name.strip())
    name_clean = re.sub(r"\s+\(\w+\)\s+\d+[a-zA-Z\*★†]?$", "", name_clean)
    name_clean = name_clean.replace("'", "")
    return name_clean.strip()

def get_scryfall_image(name, folderName):
    if name is None or "SIDEBOARD:" in name.upper():
        print("Skipping image processing for 'None' or 'SIDEBOARD:' line.")
        return

    # Extract (SET) NUMBER at the end of the string. Keep number as STRING (handles 63a, stars, etc.)
    # Examples matched: (MOM) 63, (BLC) 4, (SNC) 123a, (SET) 101★
    match = re.search(r'\((\w+)\)\s+(\S+)$', name)
    if not match:
        print("No match found for set code and collector number.")
        return

    set_code = match.group(1)           # e.g., 'MOM'
    number = match.group(2)             # e.g., '63' or '63a' or '101★'

    try:
        # Exact card via set code + collector number
        card = scrython.cards.Collector(code=set_code, collector_number=number)

        # Double-faced or modal DFC (battles, MDFC, transform, etc.)
        layout = card.layout()
        if layout in ["double_faced", "transform", "modal_dfc"]:
            faces = card.card_faces()
            front_image = faces[0]['image_uris']['png']
            back_image  = faces[1]['image_uris']['png']

            # Build nice names from the faces
            card_name_front = clean_name(faces[0]['name'])
            card_name_back  = clean_name(faces[1]['name'])

            modify_and_download_image(front_image, folderName, card_name_front)
            modify_and_download_image(back_image, folderName, card_name_back)
        else:
            # Single-faced
            front_image = card.image_uris()['png']
            card_name_front = clean_name(card.name())
            modify_and_download_image(front_image, folderName, card_name_front)

    except Exception as e:
        print(f"Failed to process '{name}': {e}")

# Example usage
#get_scryfall_image("1 Invasion of Segovia // Caetus, Sea Tyrant of Segovia (MOM) 63", "Cards")
#get_scryfall_image("1 Izzet Signet (TDC) 320", "Cards")

