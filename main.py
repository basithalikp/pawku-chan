import tkinter as tk
import time
import random
import threading
import os

# --- Local Modules (You will create these files next) ---
# We are importing them here so the main script knows they exist.
# The script will fail until you create renamer.py and rearranger.py
try:
    import renamer
    import rearranger
except ImportError:
    print("Warning: 'renamer.py' and 'rearranger.py' not found. Creating placeholder functions.")
    # Create dummy functions if the files don't exist yet, so the app can run for testing.
    class Placeholder:
        def do_nothing(self):
            print("Placeholder action: doing nothing.")
    renamer = Placeholder()
    renamer.rename_a_file = renamer.do_nothing
    rearranger = Placeholder()
    rearranger.rearrange_icons = rearranger.do_nothing


# --- Configuration ---
# The time in seconds Pawku-chan waits for you to be idle before acting.
# Set to a low number for easy testing (e.g., 15 seconds).
IDLE_TIME_SECONDS = 15

# The path to the cute cat image.
# It assumes the script is run from the root of the 'pawku-chan' folder.
ASSET_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'pawku.png')
WINDOW_WIDTH = 64  # Set to the width of your pawku.png
WINDOW_HEIGHT = 64 # Set to the height of your pawku.png


class PawkuChanApp:
    """
    The main application class that handles the GUI and the logic thread.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Pawku-chan")

        # Make the window borderless and always on top.
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", 1)

        # Position the window in the top right corner.
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - WINDOW_WIDTH - 20 # 20px padding from the edge
        y_pos = 20
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_pos}+{y_pos}')
        
        # Load the image for the avatar.
        try:
            self.pawku_image = tk.PhotoImage(file=ASSET_PATH)
            self.image_label = tk.Label(root, image=self.pawku_image, bd=0)
            self.image_label.pack()
        except tk.TclError:
            print(f"Error: Could not find image at {ASSET_PATH}. Using a placeholder.")
            # Create a fallback pink square if image is not found.
            self.image_label = tk.Label(root, bg="hotpink", width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
            self.image_label.pack()
            
        # Make the window background transparent (works on Windows/macOS, might need a compositor on Linux).
        # We use the background color of the root window as the transparency key.
        self.root.wm_attributes("-topmost", True)

        # Start the main logic in a separate thread to avoid freezing the GUI.
        self.start_chaos_thread()

    def start_chaos_thread(self):
        """Creates and starts a daemon thread to run the main logic loop."""
        chaos_thread = threading.Thread(target=self.main_logic_loop, daemon=True)
        chaos_thread.start()

    def main_logic_loop(self):
        """
        The core loop where Pawku-chan decides to act.
        This runs forever in the background.
        """
        print("Pawku-chan is watching...")
        while True:
            print(f"Pawku-chan is napping for {IDLE_TIME_SECONDS} seconds.")
            time.sleep(IDLE_TIME_SECONDS)
            
            # A list of possible actions Pawku-chan can take.
            # These are functions from your other modules.
            actions = [
                renamer.rename_a_file,
                rearranger.rearrange_icons
            ]
            
            # Randomly choose an action from the list.
            chosen_action = random.choice(actions)
            
            print(f"Pawku-chan wakes up! Choosing to '{chosen_action.__name__}'.")
            
            try:
                # Execute the chosen action.
                chosen_action()
            except Exception as e:
                print(f"Pawku-chan tried to act, but an error occurred: {e}")

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    app_root = tk.Tk()
    app = PawkuChanApp(app_root)
    # This starts the Tkinter event loop, which draws the GUI and keeps it running.
    app_root.mainloop()
