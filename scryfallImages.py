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

    try:
        # Get image URL from Scryfall
        card = scrython.cards.Named(fuzzy=name_clean)
        image_url = card.image_uris()['png']

        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()

        # Open the image and flatten transparency
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        black_bg = Image.new("RGB", img.size, (0, 0, 0))
        img_rgb = Image.alpha_composite(black_bg.convert("RGBA"), img).convert("RGB")

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
#get_scryfall_image("1 Walk-In Closet/Forgotten Cellar", "Cards")

