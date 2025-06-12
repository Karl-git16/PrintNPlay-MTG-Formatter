import os
from PIL import Image

# === Configuration ===
FOLDER = "output_sheets" 
FOLDERBACK = "output_sheets\output_sheets_backs"  
MAX_SIZE_MB = 25
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
MIN_QUALITY = 10  # Don't go below this

def compress_image(path, max_size_bytes):
    quality = 100
    while quality >= MIN_QUALITY:
        # Open the image
        with Image.open(path) as img:
            # Save to a temporary file
            temp_path = path + ".temp.jpg"
            img.save(temp_path, format='JPEG', quality=quality)

        # Check size
        if os.path.getsize(temp_path) <= max_size_bytes:
            os.replace(temp_path, path)
            print(f"Compressed '{path}' to {os.path.getsize(path)/1024/1024:.2f} MB at quality={quality}")
            return
        else:
            os.remove(temp_path)
            quality -= 5

    print(f"WARNING: Could not compress '{path}' below {MAX_SIZE_MB}MB")

def process_folder(folder):
    for filename in os.listdir(folder):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            path = os.path.join(folder, filename)
            size = os.path.getsize(path)
            if size > MAX_SIZE_BYTES:
                print(f"Compressing: {filename} ({size/1024/1024:.2f} MB)")
                compress_image(path, MAX_SIZE_BYTES)
            else:
                print(f"OK: {filename} ({size/1024/1024:.2f} MB)")


process_folder(FOLDER)
process_folder(FOLDERBACK)
