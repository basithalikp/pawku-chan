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

# --- Configuration (SCALED UP 2X) ---
HUNGER_TIMER_SECONDS = 10
RANDOM_RENAME_MIN_WAIT = 15
RANDOM_RENAME_MAX_WAIT = 50
CLOSE_BUTTON_MAX_WAIT = 10

# All window and element sizes have been doubled
WINDOW_WIDTH, WINDOW_HEIGHT = 128, 160 # Was 64, 80
METER_HEIGHT = 20 # Was 10

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
                    # Resize the GIF frames to the new, larger window width
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
        self.callout_window = None

        # --- GUI Setup ---
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x_pos = self.screen_width - WINDOW_WIDTH - 20
        self.y_pos = 20
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{self.x_pos}+{self.y_pos}')
        
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
                self.show_callout("Purrrrr...")
                self.root.after(3000, lambda: self.set_animation("idle"))

    def start_background_threads(self):
        threading.Thread(target=self.hunger_management_loop, daemon=True).start()
        threading.Thread(target=self.random_renaming_loop, daemon=True).start()
        threading.Thread(target=self.random_close_button_loop, daemon=True).start()

    def hunger_management_loop(self):
        while True:
            time.sleep(HUNGER_TIMER_SECONDS)
            with self.state_lock:
                if self.hunger_level < 3:
                    self.hunger_level += 1
                
                self.root.after(0, self.update_hunger_meter)
                
                if self.hunger_level == 1:
                    self.root.after(0, lambda: self.set_animation("hungry"))
                    self.root.after(0, lambda: self.show_callout("I'm hungry! Feed me!"))
                elif self.hunger_level == 2:
                    self.root.after(0, lambda: self.show_callout("Hmph! I'll 'tidy' this myself."))
                    rearranger.rearrange_icons()
                elif self.hunger_level == 3:
                    self.root.after(0, lambda: self.show_callout("You asked for this..."))
                    deleter.delete_a_file()

    def random_renaming_loop(self):
        while True:
            time.sleep(random.uniform(RANDOM_RENAME_MIN_WAIT, RANDOM_RENAME_MAX_WAIT))
            self.root.after(0, lambda: self.show_callout("This needs more art."))
            renamer.rename_a_file()

    def random_close_button_loop(self):
        while True:
            time.sleep(random.uniform(1, CLOSE_BUTTON_MAX_WAIT))
            self.root.after(0, self.create_close_button)

    def create_close_button(self):
        if self.close_button_window and self.close_button_window.winfo_exists():
            return
        
        # Scaled close button size
        button_size = 20
        font_size = 16
        
        self.close_button_window = tk.Toplevel(self.root)
        self.close_button_window.overrideredirect(True)
        self.close_button_window.wm_attributes("-topmost", True)
        
        x = random.randint(0, self.screen_width - button_size)
        y = random.randint(0, self.screen_height - button_size)
        self.close_button_window.geometry(f"{button_size}x{button_size}+{x}+{y}")

        close_button = tk.Button(self.close_button_window, text="X", bg="red", fg="white", font=("Arial", font_size, "bold"), command=self.quit_program, bd=0, activebackground="darkred")
        close_button.pack(expand=True, fill="both")
        self.close_button_window.after(2000, self.destroy_close_button)

    def destroy_close_button(self):
        if self.close_button_window and self.close_button_window.winfo_exists():
            self.close_button_window.destroy()
        self.close_button_window = None

    def show_callout(self, text):
        if self.callout_window and self.callout_window.winfo_exists():
            self.callout_window.destroy()

        self.callout_window = tk.Toplevel(self.root)
        self.callout_window.overrideredirect(True)
        self.callout_window.wm_attributes("-topmost", True)
        
        # Scaled callout font and padding
        label = tk.Label(
            self.callout_window, text=text, bg="lightyellow", fg="black",
            font=("Comic Sans MS", 18), wraplength=300, justify="left",
            padx=20, pady=10, relief="solid", borderwidth=1
        )
        label.pack()
        
        callout_x = self.x_pos - self.callout_window.winfo_reqwidth() - 10
        callout_y = self.y_pos
        self.callout_window.geometry(f"+{callout_x}+{callout_y}")
        self.callout_window.after(3000, self.destroy_callout)

    def destroy_callout(self):
        if self.callout_window and self.callout_window.winfo_exists():
            self.callout_window.destroy()
        self.callout_window = None

    def quit_program(self):
        print("Close button clicked! Pawku-chan vanishes.")
        self.root.destroy()

if __name__ == "__main__":
    app_root = tk.Tk()
    app = PawkuChanApp(app_root)
    app_root.mainloop()
