from PIL import Image
import os

# Settings
input_folder = 'Cards'
output_folder = 'Cards_resized'
target_size = (810, 1115)  # 12"x18" at 300 dpi
rotation_angle = 90         # degrees counter-clockwise

# Create output folder
def convert(input_folder, output_folder, target_size, rotation_angle):
    os.makedirs(output_folder, exist_ok=True)

    # Process each image
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)

            # Resize to fixed size
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)

            # Rotate image (expand=True resizes canvas to fit rotated image if needed)
            rotated_img = resized_img.rotate(rotation_angle, expand=True)

            # Save image with DPI metadata
            output_path = os.path.join(output_folder, filename)
            rotated_img.save(output_path, dpi=(300, 300))

            print(f"Resized, rotated, and saved: {output_path}")

#convert(input_folder, output_folder, target_size, rotation_angle)
