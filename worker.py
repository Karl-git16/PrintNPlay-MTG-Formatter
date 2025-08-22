# worker.py
import sys
import json
import os

def main():
    if len(sys.argv) < 2:
        print("No step provided", file=sys.stderr)
        sys.exit(2)
    
    step = sys.argv[1]
    payload = json.loads(os.environ.get("STEP_ARGS_JSON", "{}"))
    
    # Import your existing backend functions AFTER the __main__ check
    # This prevents GUI imports when running as subprocess
    from convert import convert
    from rename import rename_files
    from list import cardlist
    from movefiles import move_files
    from postprocess import process_folder
    from scryfallImages import get_scryfall_image
    from sheetMaker import create_sheet_with_images
    
    if step == "cardlist":
        cardlist(payload["input_list"], payload["output_list"], payload["output_list_back"])
    elif step == "download_batch":
        # Download a batch of card names
        for name in payload["names"]:
            try:
                get_scryfall_image(name, payload["cards_dir"])
            except Exception as e:
                print(f"DOWNLOAD_FAIL::{name}::{e}", file=sys.stderr)
    elif step == "rename":
        rename_files(payload["folder_path"])
    elif step == "movefiles":
        move_files(payload["src"], payload["backs_dir"], payload["output_list_back"])
    elif step == "convert":
        convert(payload["src"], payload["dst"], tuple(payload["size"]), payload["angle"])
    elif step == "sheets":
        create_sheet_with_images(payload["src"], payload["dst"], payload["cardlist_txt"], payload["template_pdf"])
    elif step == "postproc":
        process_folder(payload["folder"])
    else:
        print(f"Unknown step: {step}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()