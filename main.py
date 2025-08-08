import tkinter as tk
import time
import random
import threading
import os

# --- Local Modules ---
# Now importing all three logic modules.
try:
    import renamer
    import rearranger
    import deleter
except ImportError:
    print("Warning: One or more modules (renamer, rearranger, deleter) not found. Using placeholders.")
    class Placeholder:
        def do_nothing(self, *args): print("Placeholder action: doing nothing.")
    renamer = Placeholder()
    renamer.rename_a_file = renamer.do_nothing
    rearranger = Placeholder()
    rearranger.rearrange_icons = rearranger.do_nothing
    deleter = Placeholder()
    deleter.delete_a_file = deleter.do_nothing

# --- Configuration ---
HUNGER_TIMER_SECONDS = 30
RANDOM_RENAME_MIN_WAIT = 60
RANDOM_RENAME_MAX_WAIT = 180

ASSET_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'pawku.png')
WINDOW_WIDTH = 64
WINDOW_HEIGHT = 64

class PawkuChanApp:
    """
    The main application class that handles the GUI and the logic threads.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Pawku-chan")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", 1)

        # --- State Management ---
        self.hunger_level = 0 # 0:Content, 1:Hungry, 2:Mad, 3:Furious
        self.state_lock = threading.Lock()

        # --- GUI Setup ---
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - WINDOW_WIDTH - 20
        y_pos = 20
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_pos}+{y_pos}')
        
        try:
            self.pawku_image = tk.PhotoImage(file=ASSET_PATH)
            self.image_label = tk.Label(root, image=self.pawku_image, bd=0, cursor="hand2")
        except tk.TclError:
            self.image_label = tk.Label(root, bg="hotpink", width=WINDOW_WIDTH, height=WINDOW_HEIGHT, cursor="hand2")
        
        self.image_label.pack()
        self.root.wm_attributes("-transparentcolor", self.root['bg'])
        self.image_label.bind("<Button-1>", self.feed_pet)

        # --- Start Background Logic ---
        self.start_background_threads()

    def feed_pet(self, event):
        """Called when the user clicks on Pawku-chan. Resets hunger."""
        with self.state_lock:
            if self.hunger_level > 0:
                print("You fed Pawku-chan! It purrs contentedly.")
                self.hunger_level = 0

    def start_background_threads(self):
        """Starts the two separate logic threads for hunger and renaming."""
        threading.Thread(target=self.hunger_management_loop, daemon=True).start()
        threading.Thread(target=self.random_renaming_loop, daemon=True).start()

    def hunger_management_loop(self):
        """The core loop where Pawku-chan gets hungry and acts out."""
        print("Pawku-chan's hunger cycle has begun.")
        while True:
            time.sleep(HUNGER_TIMER_SECONDS)

            with self.state_lock:
                if self.hunger_level == 0: # Was content, now gets hungry
                    self.hunger_level = 1
                    print("Pawku-chan is hungry! Feed it by clicking on it.")
                
                elif self.hunger_level == 1: # Was hungry, now gets mad
                    self.hunger_level = 2
                    print("You didn't feed Pawku-chan! It's mad and rearranges your icons!")
                    try:
                        rearranger.rearrange_icons()
                    except Exception as e:
                        print(f"Error during rearrangement: {e}")

                elif self.hunger_level >= 2: # Was mad, now gets/stays furious
                    self.hunger_level = 3
                    print("Still no food! Pawku-chan is FURIOUS and deletes a file!")
                    try:
                        # *** THIS IS THE UPDATED PART ***
                        # It now calls the function from the new deleter.py module.
                        deleter.delete_a_file() 
                    except Exception as e:
                        print(f"Error during deletion: {e}")

    def random_renaming_loop(self):
        """A separate loop for the original artistic renaming feature."""
        print("Pawku-chan's artistic spirit is stirring...")
        while True:
            wait_time = random.uniform(RANDOM_RENAME_MIN_WAIT, RANDOM_RENAME_MAX_WAIT)
            time.sleep(wait_time)
            
            print("Pawku-chan feels 'artistic' and renames a file.")
            try:
                renamer.rename_a_file()
            except Exception as e:
                print(f"Error during artistic renaming: {e}")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = PawkuChanApp(app_root)
    app_root.mainloop()
