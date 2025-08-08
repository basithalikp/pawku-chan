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
CLOSE_BUTTON_MAX_WAIT = 10

WINDOW_WIDTH, WINDOW_HEIGHT = 64, 80
METER_HEIGHT = 10

class AnimatedGIF:
    """Helper class for animated GIFs."""
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
                    frame = ImageTk.PhotoImage(img.copy().resize((WINDOW_WIDTH, WINDOW_WIDTH)))
                    self.frames.append(frame)
        except Exception as e:
            fallback_img = Image.new('RGBA', (WINDOW_WIDTH, WINDOW_WIDTH), 'hotpink')
            self.frames.append(ImageTk.PhotoImage(fallback_img))

    def play(self, label):
        self.label = label
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
        self._animate(0)

    def _animate(self, frame_num):
        if not self.label or not self.label.winfo_exists(): return
        frame = self.frames[frame_num]
        self.label.config(image=frame)
        next_frame_num = (frame_num + 1) % len(self.frames)
        self.animation_job = self.root.after(self.delay, self._animate, next_frame_num)

class PawkuChanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pawku-chan")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        self.hunger_level = 0
        self.state_lock = threading.Lock()
        self.current_animation = None
        self.close_button_window = None

        # --- GUI Setup ---
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - WINDOW_WIDTH - 20
        y_pos = 20
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_pos}+{y_pos}')
        
        self.image_label = tk.Label(root, bd=0, cursor="hand2")
        self.image_label.pack()
        self.image_label.bind("<Button-1>", self.feed_pet)

        self.hunger_canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=METER_HEIGHT, bg='gray20', highlightthickness=0)
        self.hunger_canvas.pack()
        
        self.animations = {
            "idle": AnimatedGIF(root, os.path.join('assets', 'idle.gif')),
            "hungry": AnimatedGIF(root, os.path.join('assets', 'hungry.gif')),
            "purring": AnimatedGIF(root, os.path.join('assets', 'purring.gif'))
        }

        self.set_animation("idle")
        self.update_hunger_meter()
        self.start_background_threads()

    def update_hunger_meter(self):
        self.hunger_canvas.delete("all")
        states = {0: ("green", 1.0), 1: ("yellow", 0.66), 2: ("orange", 0.33), 3: ("red", 0.1)}
        color, width_percent = states.get(self.hunger_level, states[3])
        bar_width = WINDOW_WIDTH * width_percent
        self.hunger_canvas.create_rectangle(0, 0, bar_width, METER_HEIGHT, fill=color, outline="")

    def set_animation(self, state):
        if state != self.current_animation and state in self.animations:
            self.current_animation = state
            self.animations[state].play(self.image_label)

    def feed_pet(self, event):
        with self.state_lock:
            if self.hunger_level > 0:
                self.hunger_level = 0
                self.update_hunger_meter()
                self.set_animation("purring")
                self.root.after(3000, lambda: self.set_animation("idle"))

    def start_background_threads(self):
        threading.Thread(target=self.hunger_management_loop, daemon=True).start()
        threading.Thread(target=self.random_renaming_loop, daemon=True).start()
        threading.Thread(target=self.random_close_button_loop, daemon=True).start()

    def hunger_management_loop(self):
        """Manages hunger and its consequences safely."""
        while True:
            time.sleep(HUNGER_TIMER_SECONDS)
            with self.state_lock:
                if self.hunger_level < 3:
                    self.hunger_level += 1
                
                # --- THREAD-SAFE GUI UPDATES ---
                # Ask the main thread to update the GUI instead of doing it directly.
                self.root.after(0, self.update_hunger_meter)
                
                if self.hunger_level == 1:
                    self.root.after(0, lambda: self.set_animation("hungry"))
                elif self.hunger_level == 2:
                    print("Pawku-chan is mad and rearranges your icons!")
                    rearranger.rearrange_icons()
                elif self.hunger_level == 3:
                    print("Pawku-chan is FURIOUS and deletes a file!")
                    deleter.delete_a_file()

    def random_renaming_loop(self):
        """Manages random file renaming."""
        while True:
            time.sleep(random.uniform(RANDOM_RENAME_MIN_WAIT, RANDOM_RENAME_MAX_WAIT))
            print("Pawku-chan feels 'artistic' and renames a file.")
            renamer.rename_a_file()

    def random_close_button_loop(self):
        """Periodically asks the main thread to create the close button."""
        while True:
            time.sleep(random.uniform(1, CLOSE_BUTTON_MAX_WAIT))
            self.root.after(0, self.create_close_button)

    def create_close_button(self):
        """Creates the close button. Runs only in the main thread."""
        if self.close_button_window and self.close_button_window.winfo_exists():
            return

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.close_button_window = tk.Toplevel(self.root)
        self.close_button_window.overrideredirect(True)
        self.close_button_window.wm_attributes("-topmost", True)
        
        x_pos = random.randint(0, screen_width - 30)
        y_pos = random.randint(0, screen_height - 30)
        self.close_button_window.geometry(f"30x30+{x_pos}+{y_pos}")

        close_button = tk.Button(
            self.close_button_window, text="X", bg="red", fg="white",
            font=("Arial", 12, "bold"), command=self.quit_program, bd=0,
            activebackground="darkred"
        )
        close_button.pack(expand=True, fill="both")

        self.close_button_window.after(2000, self.destroy_close_button)

    def destroy_close_button(self):
        """Safely destroys the close button window."""
        if self.close_button_window and self.close_button_window.winfo_exists():
            self.close_button_window.destroy()
        self.close_button_window = None

    def quit_program(self):
        """Destroys the main window, exiting the program."""
        print("Close button clicked! Pawku-chan vanishes.")
        self.root.destroy()

if __name__ == "__main__":
    app_root = tk.Tk()
    app = PawkuChanApp(app_root)
    app_root.mainloop()
