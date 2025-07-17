import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import shutil
import sys
import time

# Placeholder backend functions
from convert import convert
from rename import rename_files
from list import cardlist
from movefiles import move_files
from postprocess import process_folder
from scryfallImages import get_scryfall_image
from webDriver import automate_browser
from PIL import Image, ImageTk, ImageSequence

#------------------------ Backend Configuration ------------------------#
input_list = "decklist.txt"
output_list = "cardlist.txt"
output_list_back = "cardlistback.txt"

folder_path = r'Cards'
folder_resized = r'Cards_resized'
folder_resized_back = r'Cardbacks_resized'
FOLDER = "output_sheets"
FOLDERBACK = r"output_sheets\output_sheets_backs"

target_size = (810, 1115)
rotation_angle = 270
rotation_angle_back = 90

def find_resource(path):
    """ Return the absolute path to a bundled resource (e.g., Cards.jsx) """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.abspath(path)
folder_path_back = find_resource("Cardbacks")

def find_photoshop():
    possible_paths = [
        r"C:\Program Files\Adobe\Adobe Photoshop 2025\Photoshop.exe",
        r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe",
        r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",
        r"C:\Program Files\Adobe\Adobe Photoshop 2022\Photoshop.exe",
        r"C:\Program Files (x86)\Adobe\Adobe Photoshop\Photoshop.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found Photoshop at: {path}")
            return path
    
    print("❌ Photoshop not found in default locations.")
    return None

def process_cards(type):
    #For automated mode
    if(type == "automated"):
        print("Processing cards in automated mode...")
        # Read each line from decklist.txt and call get_scryfall_image
        with open("decklist.txt", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:  # skip empty lines
                    get_scryfall_image(line, "Cards")

    cardlist(input_list, output_list, output_list_back)
    rename_files(folder_path)
    move_files(folder_path, folder_path_back, output_list_back)
    convert(folder_path, folder_resized, target_size, rotation_angle)
    convert(folder_path_back, folder_resized_back, target_size, rotation_angle_back)

    photoshop_path = find_photoshop()
    script_path = find_resource("Cards.jsx")

    # Launch Photoshop script
    subprocess.Popen([photoshop_path, script_path])

    # Wait for the flag
    flag_path = os.path.join(os.path.dirname(script_path), "done.flag")
    timeout = 300  # max wait time in seconds
    waited = 0

    while not os.path.exists(flag_path) and waited < timeout:
        time.sleep(2)
        waited += 2

    if os.path.exists(flag_path):
        print("✅ Photoshop script completed. Terminating Photoshop.")
        subprocess.run(["taskkill", "/IM", "Photoshop.exe", "/F"])
        os.remove(flag_path)  # cleanup
    else:
        print("⚠️ Timeout waiting for Photoshop script to complete.")

    process_folder(FOLDER)
    process_folder(FOLDERBACK)

#------------------------ Tkinter Frontend ------------------------#
def cleanup_and_exit(app):
    import glob

    try:
        # Delete cardlist files
        for file in ["cardlist.txt", "cardlistback.txt", "decklist.txt"]:
            if os.path.exists(file):
                os.remove(file)
                print(f"🗑️ Deleted {file}")

        # Delete all files in 'Cards'
        if os.path.exists("Cards"):
            for file in os.listdir("Cards"):
                path = os.path.join("Cards", file)
                if os.path.isfile(path):
                    os.remove(path)
                    print(f"🗑️ Deleted Cards/{file}")

        # Delete everything in 'Cardbacks' except "Card Back.png"
        if os.path.exists("Cardbacks"):
            for file in os.listdir("Cardbacks"):
                if file != "Card Back.jpg":
                    path = os.path.join("Cardbacks", file)
                    if os.path.isfile(path):
                        os.remove(path)
                        print(f"🗑️ Deleted Cardbacks/{file}")

        # Delete all files in 'Cards_resized' and 'Cardbacks_resized'
        for folder in ["Cards_resized", "Cardbacks_resized"]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    path = os.path.join(folder, file)
                    if os.path.isfile(path):
                        os.remove(path)
                        print(f"🗑️ Deleted {folder}/{file}")
        # Delete all files in 'output_sheets' and 'output_sheets_backs'
        for folder in ["output_sheets", "output_sheets/output_sheets_backs"]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    path = os.path.join(folder, file)
                    if os.path.isfile(path):
                        os.remove(path)
                        print(f"🗑️ Deleted {folder}/{file}")

        print("✅ Cleanup complete. Exiting application.")
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")

    app.quit()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MTG Proxy Automation")
        self.geometry("800x600")
        self.configure(bg="black")  
        self.type = "automated"

        container = tk.Frame(self, bg="black")
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (StartScreen, infoScreen, FirstScreen, ManualScreen, ManualScreen2, AutomatedScreen, StartProcessingScreen, orderScreen):
            frame = F(container, self)
            self.frames[F] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_frame(StartScreen)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Card Images",
            filetypes=[("Image Files", "*.jpg *.png")]
        )
        if file_paths:
            target_folder = "Cards"
            os.makedirs(target_folder, exist_ok=True)
            print("Selected files:")
            for path in file_paths:
                filename = os.path.basename(path)
                destination = os.path.join(target_folder, filename)
                shutil.move(path, destination)
                print(f"✅ Moved to: {destination}")

    def change_type(self, type):
        self.type = type
        print(f"Automated mode set to: " + type)

class StartScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        tk.Label(self, text="MTG Pr oxy Automation", font=("Arial", 32), bg="black", fg="white").pack(pady=60)
        tk.Button(self, text="Click to start", command=lambda: controller.show_frame(infoScreen),
                  bg="green", fg="white", font=("Arial", 14)).pack(pady=20)
        
class infoScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        tk.Label(self, text="MTG Proxy Automation - Rules & Info", font=("Arial", 20, "bold"),
                 bg="black", fg="white").pack(pady=20)

        rules = [
            "1.) You must have Photoshop installed.",
            "2.) If you choose Manual (MPCFILL), do NOT include the card back image.",
            "3.) Automated mode pulls images from Scryfall — no fancy art or alters.",
            "4.) You must have a Print & Play account.",
            "5.) Recommended to put the app in a folder, because the app will create folders.",
            "6.) If the print is wrong... unlucky :\\"
        ]

        for rule in rules:
            tk.Label(self, text=rule, font=("Arial", 14), bg="black", fg="white", anchor="w", justify="left").pack(pady=3)

        tk.Button(self, text="Back", command=lambda: controller.show_frame(StartScreen),
                  bg="orange", fg="black", font=("Arial", 12)).pack(pady=15)

        tk.Button(self, text="Next", command=lambda: controller.show_frame(FirstScreen),
                  bg="green", fg="white", font=("Arial", 12)).pack()

        
class FirstScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        tk.Label(self, text="How do you want your card images uploaded?", font=("Arial", 18),
                 bg="black", fg="white").pack(pady=40)

        button_frame = tk.Frame(self, bg="black")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Manual (MPCFILL)",
                  command=lambda: [controller.show_frame(ManualScreen), controller.change_type("manual")],
                  bg="red", fg="white", font=("Arial", 12), width=20).pack(side="left", padx=30)

        tk.Button(button_frame, text="Automated (Scryfall)",
                  command=lambda: [controller.show_frame(AutomatedScreen), controller.change_type("automated")],
                  bg="blue", fg="white", font=("Arial", 12), width=20).pack(side="right", padx=30)

        tk.Button(self, text="Back", command=lambda: controller.show_frame(infoScreen),
                  bg="orange", fg="black", font=("Arial", 12)).pack(pady=10)

class ManualScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        tk.Label(self, text="Paste Your Decklist Below", font=("Arial", 18), bg="black", fg="white").pack(pady=20)

        self.decklist_box = tk.Text(self, width=50, height=10, font=("Arial", 12))
        self.decklist_box.pack(pady=10)

        tk.Button(self, text="Submit Decklist",
                  command=lambda: [self.submit_decklist(), controller.show_frame(ManualScreen2)],
                  bg="white", font=("Arial", 12)).pack(pady=10)

        tk.Button(self, text="Back", command=lambda: controller.show_frame(FirstScreen),
                  bg="orange", fg="black", font=("Arial", 12)).pack(pady=10)

    def submit_decklist(self):
        decklist = self.decklist_box.get("1.0", tk.END).strip()
        if decklist:
            with open("decklist.txt", "w", encoding="utf-8") as f:
                f.write(decklist)
            print("✅ Decklist saved to decklist.txt")
        else:
            print("⚠️ Decklist is empty.")

class ManualScreen2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        tk.Label(self, text="Upload Card Images From MPCFILL", font=("Arial", 18), bg="black", fg="white").pack(pady=30)

        tk.Button(self, text="Select Image Files",
                  command=controller.select_files,
                  bg="white", font=("Arial", 12)).pack(pady=20)

        tk.Button(self, text="Start Processing",
                  command=process_cards,
                  bg="green", fg="white", font=("Arial", 12)).pack(pady=10)

        tk.Button(self, text="Back", command=lambda: controller.show_frame(ManualScreen),
                  bg="orange", fg="black", font=("Arial", 12)).pack(pady=10)

class AutomatedScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        tk.Label(self, text="Paste Your Decklist Below", font=("Arial", 18), bg="black", fg="white").pack(pady=20)

        self.decklist_box = tk.Text(self, width=50, height=10, font=("Arial", 12))
        self.decklist_box.pack(pady=10)

        tk.Button(self, text="Submit Decklist",
                  command=lambda: [self.submit_decklist(), controller.show_frame(StartProcessingScreen)],
                  bg="white", font=("Arial", 12)).pack(pady=10)

        tk.Button(self, text="Back", command=lambda: controller.show_frame(FirstScreen),
                  bg="orange", fg="black", font=("Arial", 12)).pack(pady=10)
        
    def submit_decklist(self):
        decklist = self.decklist_box.get("1.0", tk.END).strip()
        if decklist:
            with open("decklist.txt", "w", encoding="utf-8") as f:
                f.write(decklist)
            print("✅ Decklist saved to decklist.txt")
        else:
            print("⚠️ Decklist is empty.")
        
class StartProcessingScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")

        tk.Label(self, text="Click to Start Processing", font=("Arial", 18), bg="black", fg="white").pack(pady=20)

        self.status_label = None  # This will hold the "Processing..." label

        tk.Button(self, text="Start Processing",
                  command=lambda: self.start_processing(controller),
                  bg="green", fg="white", font=("Arial", 12)).pack(pady=10)

    def start_processing(self, controller):
        # Show "Processing..." label
        if self.status_label is None:
            self.status_label = tk.Label(self, text="Processing...", font=("Arial", 14), fg="white", bg="black")
            self.status_label.pack(pady=10)

        self.after(100, lambda: self.run_processing(controller))

    def run_processing(self, controller):
        process_cards(controller.type)

        # Remove the status label
        if self.status_label:
            self.status_label.destroy()
            self.status_label = None

        controller.show_frame(orderScreen)


class orderScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        tk.Label(self, text="Enter Username and Password", font=("Arial", 18), bg="black", fg="white").pack(pady=20)
        self.username_entry = tk.Entry(self, font=("Arial", 14))
        self.username_entry.pack(pady=10)
        self.password_entry = tk.Entry(self, show='*', font=("Arial", 14))
        self.password_entry.pack(pady=10)
        tk.Button(self, text="Submit",
                  command=lambda: [automate_browser(FOLDER, FOLDERBACK, self.username_entry.get(), self.password_entry.get()),
                                   controller.show_frame(StartScreen)],
                  bg="blue", fg="white", font=("Arial", 12)).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: controller.show_frame(StartProcessingScreen),
                  bg="orange", fg="black", font=("Arial", 12)).pack(pady=10)
        tk.Button(self, text="Exit", command=lambda: cleanup_and_exit(controller),
                bg="red", fg="white", font=("Arial", 12)).pack(pady=10)



#------------------------ Launch App ------------------------#
if __name__ == "__main__":
    app = App()
    app.mainloop()
