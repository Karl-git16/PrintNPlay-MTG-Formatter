from PIL import Image, ImageOps
from io import BytesIO
import scrython
import requests
import re
import os
from rename import sanitize_filename

def get_scryfall_image(name, folderName):
    if name is None or "SIDEBOARD:" in name.upper():
        print("⚠️ Skipping image processing for 'None' or 'SIDEBOARD:' line.")
        return

    # Remove quantity prefix like "1 Aetherize"
    name_clean = re.sub(r"^\d+\s+", "", name.strip())
    name_clean = re.sub(r"\s+\(\w+\)\s+\d+$", "", name_clean)
    name_clean = name_clean.replace("'", "")
    match = re.search(r'\((\w+)\)\s+(\d+)$', name)

    if match:
        set_code = match.group(1)  # 'BLC'
        number = int(match.group(2))  # 4
    else:
        print("No match found.")

    try:
        # Get image URL from Scryfall
        #card = scrython.cards.Named(fuzzy=name_clean)
        card_image_name = scrython.cards.Collector(code=set_code, collector_number=number)
        image_url = card_image_name.image_uris()['png']

        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()

        # Open image and ensure it's RGBA
        img = Image.open(BytesIO(response.content)).convert("RGBA")

        # Get pixel data
        pixels = img.getdata()

        # Replace partially transparent pixels with black
        new_pixels = []
        for pixel in pixels:
            r, g, b, a = pixel
            if a < 255:  # transparent or semi-transparent
                new_pixels.append((0, 0, 0, 255))  # fully black
            else:
                new_pixels.append((r, g, b, 255))  # keep as-is

        # Apply modified pixels
        img.putdata(new_pixels)

        # Now convert to RGB and add border
        img_rgb = img.convert("RGB")
        border_size = 38
        img_with_border = ImageOps.expand(img_rgb, border=border_size, fill='black')

        # Add black border
        border_size = 38
        img_with_border = ImageOps.expand(img_rgb, border=border_size, fill='black')
        name_clean = sanitize_filename(name_clean, name_clean)  # Ensure we sanitize the filename
        # Save to 'cards' folder
        os.makedirs(folderName, exist_ok=True)
        save_path = os.path.join(folderName, name_clean + ".jpg")
        img_with_border.save(save_path)
        print(f"✅ Saved image: {save_path}")

    except Exception as e:
        print(f"❌ Failed to process '{name}': {e}")

# Example usage
#get_scryfall_image("1 Training Center (CMM) 434", "Cards")

