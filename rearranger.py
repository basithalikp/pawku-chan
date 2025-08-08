import subprocess
import os
import random

def get_desktop_files():
    """Returns a list of non-hidden files and folders on the desktop."""
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    try:
        all_items = os.listdir(desktop_path)
        # Filter out hidden files (those starting with a dot)
        visible_items = [item for item in all_items if not item.startswith('.')]
        return visible_items
    except FileNotFoundError:
        print(f"Error: Desktop path not found.")
        return []

def rearrange_icons():
    """
    Rearranges desktop icons into a random "splatter" formation.
    This function uses the 'gio' command-line tool, which is standard on modern
    GNOME desktops (like Ubuntu).
    """
    print("Attempting to rearrange icons...")
    desktop_files = get_desktop_files()
    if not desktop_files:
        print("No icons found on the desktop to rearrange.")
        return

    # A simple (and bad) way to get screen resolution.
    try:
        res_cmd = "xrandr | grep '*' | head -n 1 | awk '{print $1}'"
        res_proc = subprocess.run(res_cmd, shell=True, capture_output=True, text=True, check=True)
        width, height = map(int, res_proc.stdout.strip().split('x'))
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Could not determine screen resolution, using fallback. Error: {e}")
        width, height = 1920, 1080 # Fallback resolution

    print(f"Detected screen resolution: {width}x{height}")

    for i, filename in enumerate(desktop_files):
        # Generate random coordinates for the icon.
        # We give it some padding so icons don't go completely off-screen.
        x_pos = random.randint(0, width - 100)
        y_pos = random.randint(0, height - 150)

        # The 'gio set' command sets metadata on a file.
        # The 'metadata::nautilus-icon-position' key is what GNOME uses to store
        # the icon's location on the desktop.
        # We construct the command for each file.
        command = f"gio set -t string \"file://{os.path.join(os.path.expanduser('~'), 'Desktop', filename)}\" metadata::nautilus-icon-position \"{x_pos},{y_pos}\""
        
        try:
            # Execute the command.
            # `shell=True` is necessary here.
            # `capture_output=True` hides the command's output from our terminal.
            subprocess.run(command, shell=True, check=True, capture_output=True)
            print(f"Moved '{filename}' to ({x_pos}, {y_pos})")
        except subprocess.CalledProcessError as e:
            print(f"Failed to move icon for '{filename}'.")
            print(f"Error: {e.stderr.decode()}")
        except Exception as e:
            print(f"An unexpected error occurred while moving '{filename}': {e}")
            
if __name__ == '__main__':
    # This allows you to test the script directly.
    # Run 'python3 rearranger.py' in your terminal.
    print("Testing the rearranger module...")
    rearrange_icons()
