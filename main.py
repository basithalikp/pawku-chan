import tkinter as tk
import time
import random
import threading
import os
from PIL import Image, ImageTk

# --- Local Modules ---
try:
    import renamer
    import rearranger
    import deleter
except ImportError:
    print("Warning: One or more modules not found. Using placeholders.")
    class Placeholder:
        def do_nothing(self, *args): print("Placeholder action.")
    renamer, rearranger, deleter = Placeholder(), Placeholder(), Placeholder()
    renamer.rename_a_file = rearranger.rearrange_icons = deleter.delete_a_file = renamer.do_nothing

# --- Configuration ---
HUNGER_TIMER_SECONDS = 30
RANDOM_RENAME_MIN_WAIT = 60
RANDOM_RENAME_MAX_WAIT = 180

# Adjust window size to make space for the hunger meter
WINDOW_WIDTH, WINDOW_HEIGHT = 64, 80 # Increased height
METER_HEIGHT = 10 # Height of the hunger bar

class AnimatedGIF:
    """A helper class to handle loading and playing animated GIFs in Tkinter."""
    def __init__(self, root, path):
        self.root = root
        self.path = path
        self.frames = []
        self.delay = 100
        self.label = None
        self.animation_job = None
        self._load()

    def _load(self):
        try:
            with Image.open(self.path) as img:
                self.delay = img.info.get('duration', 100)
                for i in range(img.n_frames):
                    img.seek(i)
                    frame = ImageTk.PhotoImage(img.copy().resize((WINDOW_WIDTH, WINDOW_WIDTH))) # Ensure GIF is square
                    self.frames.append(frame)
        except Exception as e:
            print(f"Error loading GIF {self.path}: {e}")
            fallback_img = Image.new('RGBA', (WINDOW_WIDTH, WINDOW_WIDTH), 'hotpink')
            self.frames.append(ImageTk.PhotoImage(fallback_img))

    def play(self, label):
        self.label = label
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
        self._animate(0)

    def _animate(self, frame_num):
        if not self.label: return
        frame = self.frames[frame_num]
        self.label.config(image=frame)
        next_frame_num = (frame_num + 1) % len(self.frames)
        self.animation_job = self.root.after(self.delay, self._animate, next_frame_num)

class PawkuChanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pawku-chan")
        self.root.overrideredirect(True)
        # As requested, using -topmost instead of -transparentcolor for better compatibility.
        self.root.wm_attributes("-topmost", True) 

        self.hunger_level = 0
        self.state_lock = threading.Lock()
        self.current_animation = None

        # --- GUI Setup ---
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - WINDOW_WIDTH - 20
        y_pos = 20
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_pos}+{y_pos}')
        
        self.image_label = tk.Label(root, bd=0, cursor="hand2")
        self.image_label.pack()
        self.image_label.bind("<Button-1>", self.feed_pet)

        # --- Hunger Meter Canvas ---
        self.hunger_canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=METER_HEIGHT, bg='gray20', highlightthickness=0)
        self.hunger_canvas.pack()
        
        # --- Load Animations ---
        self.animations = {
            "idle": AnimatedGIF(root, os.path.join('assets', 'idle.gif')),
            "hungry": AnimatedGIF(root, os.path.join('assets', 'hungry.gif')),
            "purring": AnimatedGIF(root, os.path.join('assets', 'purring.gif'))
        }

        self.set_animation("idle")
        self.update_hunger_meter() # Draw the initial full hunger bar
        self.start_background_threads()

    def update_hunger_meter(self):
        """Redraws the hunger bar based on the current hunger level."""
        self.hunger_canvas.delete("all") # Clear the canvas
        
        # Define colors and widths for each hunger level
        hunger_states = {
            0: {"color": "green", "width_percent": 1.0},    # Content
            1: {"color": "yellow", "width_percent": 0.66},   # Hungry
            2: {"color": "orange", "width_percent": 0.33},   # Mad
            3: {"color": "red", "width_percent": 0.1}       # Furious
        }
        
        state = hunger_states.get(self.hunger_level, hunger_states[3]) # Default to furious state
        bar_width = WINDOW_WIDTH * state["width_percent"]
        
        self.hunger_canvas.create_rectangle(0, 0, bar_width, METER_HEIGHT, fill=state["color"], outline="")

    def set_animation(self, state):
        if state != self.current_animation and state in self.animations:
            self.current_animation = state
            self.animations[state].play(self.image_label)

    def feed_pet(self, event):
        with self.state_lock:
            if self.hunger_level > 0:
                print("You fed Pawku-chan!")
                self.hunger_level = 0
                self.update_hunger_meter() # Update the meter visually
                self.set_animation("purring")
                self.root.after(3000, lambda: self.set_animation("idle"))

    def start_background_threads(self):
        threading.Thread(target=self.hunger_management_loop, daemon=True).start()
        threading.Thread(target=self.random_renaming_loop, daemon=True).start()

    def hunger_management_loop(self):
        while True:
            time.sleep(HUNGER_TIMER_SECONDS)
            with self.state_lock:
                if self.hunger_level < 3:
                    self.hunger_level += 1
                
                self.update_hunger_meter() # Update meter every time level changes
                
                if self.hunger_level == 1:
                    print("Pawku-chan is hungry!")
                    self.set_animation("hungry")
                elif self.hunger_level == 2:
                    print("Pawku-chan is mad and rearranges your icons!")
                    rearranger.rearrange_icons()
                elif self.hunger_level == 3:
                    print("Pawku-chan is FURIOUS and deletes a file!")
                    deleter.delete_a_file()

    def random_renaming_loop(self):
        while True:
            wait_time = random.uniform(RANDOM_RENAME_MIN_WAIT, RANDOM_RENAME_MAX_WAIT)
            time.sleep(wait_time)
            print("Pawku-chan feels 'artistic' and renames a file.")
            renamer.rename_a_file()

if __name__ == "__main__":
    app_root = tk.Tk()
    app = PawkuChanApp(app_root)
    app_root.mainloop()
