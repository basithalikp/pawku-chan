import os
import random
import subprocess

# --- Configuration ---
DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'changes.log')

def delete_a_file():
    """
    Finds a random file on the desktop and moves it to the system trash.
    This is much safer than os.remove().
    """
    try:
        # Get a list of all items on the desktop.
        all_items = os.listdir(DESKTOP_PATH)
        
        # Filter this list to only include files, not directories.
        files = [f for f in all_items if os.path.isfile(os.path.join(DESKTOP_PATH, f))]
        
        # Exclude hidden files and other critical project files.
        files_to_delete = [f for f in files if not f.startswith('.') and f not in ['changes.log', 'undo.py']]

        if not files_to_delete:
            print("Pawku-chan, in its rage, found no files to delete.")
            return

        # Choose a random file to be the victim.
        chosen_file = random.choice(files_to_delete)
        full_path = os.path.join(DESKTOP_PATH, chosen_file)

        # Use the 'gio trash' command, which is the standard way to trash files on Linux.
        # This is safer as it allows the user to recover the file.
        command = f"gio trash \"{full_path}\""
        subprocess.run(command, shell=True, check=True, capture_output=True)
        
        print(f"Pawku-chan, in a rage, moved '{chosen_file}' to the trash.")
        
        # Log this destructive action so the user knows what happened.
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"DELETED,{full_path}\n")

    except FileNotFoundError:
        print(f"Error: Desktop path not found at {DESKTOP_PATH}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to move '{chosen_file}' to trash. Error: {e.stderr.decode()}")
    except Exception as e:
        print(f"An unexpected error occurred in delete_a_file: {e}")

if __name__ == '__main__':
    # This allows you to test the script directly from the terminal.
    print("Testing the deleter module...")
    delete_a_file()
