import fitz  # PyMuPDF
import shutil
import os

original_pdf = "template.pdf"
input_folder = "Cards_resized"
output_folder = "output_sheets"
cardlist_file = "cardlist.txt"

# Create output directory if it doesn't exist

def create_sheet_with_images(input_folder, output_folder, cardlist_file, template_pdf="template.pdf"):
    os.makedirs(output_folder, exist_ok=True)
    # Define grid positions (3x6 = 18 cards)
    x0_list = [28, 298, 568]
    x1_list = [296, 566, 836]
    y0_list = [54, 253, 451, 649, 847, 1045]
    y1_list = [251, 449, 647, 845, 1043, 1241]

    grid_boxes = [(x0, x1, y0, y1) for y0, y1 in zip(y0_list, y1_list) for x0, x1 in zip(x0_list, x1_list)]
    max_cards_per_sheet = len(grid_boxes)

    # Read card list
    with open(cardlist_file, "r") as file:
        cards = [line.strip() for line in file]

    extensions = ['.jpg', '.jpeg', '.png']
    total_cards = len(cards)
    sheet_count = 1
    card_index = 0

    while card_index < total_cards:
        # Copy template and open new sheet
        sheet_pdf = os.path.join(output_folder, f"Sheet{sheet_count}.pdf")
        shutil.copyfile(template_pdf, sheet_pdf)
        doc = fitz.open(sheet_pdf)
        page = doc[0]
        page_rect = page.rect  # Gets the full page size
        page.draw_rect(page_rect, fill=(1, 1, 1), color=None)  # color=None avoids drawing a border

        # Add up to 18 cards to this sheet
        for box_index in range(max_cards_per_sheet):
            if card_index >= total_cards:
                break

            # Try to find image file
            card_name = cards[card_index]
            image_path = None
            for ext in extensions:
                test_path = os.path.join(input_folder, card_name + ext)
                if os.path.exists(test_path):
                    image_path = test_path
                    break

            if not image_path:
                print(f"❌ Image not found for: {card_name}")
                card_index += 1
                continue

            # Place image in grid
            x0, x1, y0, y1 = grid_boxes[box_index]
            rect = fitz.Rect(x0, y0, x1, y1)
            page.insert_image(rect, filename=image_path)
            print(f"✅ Sheet{sheet_count}: Inserted {card_name} at {rect}")
            card_index += 1

        # Save and export sheet as JPG
        doc.saveIncr()
        pix = page.get_pixmap(dpi=300)
        jpg_path = os.path.join(output_folder, f"Sheet{sheet_count}.jpg")
        pix.save(jpg_path)
        doc.close()
        os.remove(sheet_pdf)

        sheet_count += 1

#create_sheet_with_images(input_folder, output_folder, cardlist_file)
#print("✅ All sheets created successfully.")
