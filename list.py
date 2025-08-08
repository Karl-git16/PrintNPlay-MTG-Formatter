import scrython
import re
import math
from rename import sanitize_filename

# === CONFIGURE ===
input_file = "decklist.txt"
output_file = "cardlist.txt"
back_output_file = "cardlistback.txt"

def mirror_column(col_index):
    return 2 - col_index  # For 3 columns: 0 ↔ 2, 1 ↔ 1

def cardlist(input_file, output_file, back_output_file):
    # Step 1: Expand the input list
    expanded_list = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            match = re.match(r"(\d+)[xX]?\s+(.+?)(?:\s+\([A-Z0-9]+\)\s+\d+)?$", line)

            if not match:
                print(f"Skipping malformed line: {line}")
                continue

            count = int(match.group(1))
            raw_name = match.group(2).strip()
            name = raw_name.split("//")[0].strip().replace("'", "")

            if "//" in name:
                name = name.split("//", 1)[0].strip()

            for _ in range(count):
                expanded_list.append(name)

    # Step 2: Fetch card names and determine backs
    card_pairs = []
    for name in expanded_list:
        try:
            card = scrython.cards.Named(fuzzy=name)
            name_field = card.name()
            official_name = name_field.split("//")[0].strip().replace("'", "")
            layout = card.layout()

            if layout in ["double_faced", "transform", "modal_dfc"]:
                back = name_field.split("//")[1].strip().replace("'", "") if "//" in name_field else "Card Back"
            else:
                back = "Card Back"

            card_pairs.append((official_name, back))

        except scrython.exceptions.ScrythonException as e:
            print(f"Error fetching '{name}': {e}")
            card_pairs.append((name, "Card Back"))


    # Step 3: Process in 6x3 pages (18 cards per page)
    cards_per_page = 18
    total_cards = len(card_pairs)
    total_pages = math.ceil(total_cards / cards_per_page)

    all_fronts = []
    all_backs = []

    for page in range(total_pages):
        page_pairs = card_pairs[page * cards_per_page : (page + 1) * cards_per_page]

        # Initialize 6x3 grid
        grid = [[None for _ in range(3)] for _ in range(6)]
        back_grid = [["Card Back" for _ in range(3)] for _ in range(6)]

        index = 0
        for row in range(6):
            for col in range(3):
                if index >= len(page_pairs):
                    break
                front, back = page_pairs[index]
                grid[row][col] = front

                if back != "Card Back":
                    mirror_col = mirror_column(col)
                    back_grid[row][mirror_col] = back

                index += 1

        # Flatten and append to overall lists
        for row in range(6):
            for col in range(3):
                if grid[row][col] is not None:
                    all_fronts.append(grid[row][col])
                    all_backs.append(back_grid[row][col])

    # Step 4: Write outputs
    with open(output_file, 'w', encoding='utf-8') as f_out, open(back_output_file, 'w', encoding='utf-8') as b_out: 
        for front, back in zip(all_fronts, all_backs):
            sanitized_front = sanitize_filename(front, front)
            sanitized_back = sanitize_filename(back, back)
            f_out.write(sanitized_front + "\n")
            b_out.write(sanitized_back + "\n")


    print(f"{total_cards} cards processed into {total_pages} page(s).")
    print(f"Fronts written to {output_file}")
    print(f"Backs written to {back_output_file}")

#run the function
#cardlist(input_file, output_file, back_output_file)

