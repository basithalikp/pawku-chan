import os
import random

# --- Configuration ---
# The path to the user's desktop. os.path.expanduser('~') gets the user's home directory.
DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'changes.log')

# --- Word Banks for Pretentious Names ---
ADJECTIVES = [
    "Ephemeral", "Liminal", "Juxtaposed", "Laconic", "Penumbral", "Chromatic",
    "Stochastic", "Asymptotic", "Sonorous", "Deconstructed", "Silent", "Forgotten",
    "Hollow", "Radiant", "Fleeting", "Sublime", "Austere", "Fragmented"
]

NOUNS = [
    "Void", "Agony", "Serenity", "Fragmentation", "Echo", "Simulacrum",
    "Palimpsest", "Nostalgia", "Absence", "Entropy", "Silence", "Dream",
    "Memory", "Ruin", "Petal", "Path", "Whisper", "Horizon"
]

def log_change(original_path, new_path):
    """Appends a record of the file rename to the log file."""
    try:
        # 'a' mode appends to the file. We store the full paths.
        with open(LOG_FILE_PATH, 'a') as log_file:
            # We use a simple comma-separated format.
            log_file.write(f"{original_path},{new_path}\n")
    except Exception as e:
        print(f"Error: Could not write to log file at {LOG_FILE_PATH}: {e}")

def rename_a_file():
    """
    Finds a random file on the desktop and renames it to something artistic.
    """
    try:
        # Get a list of all items on the desktop.
        all_items = os.listdir(DESKTOP_PATH)
        
        # Filter this list to only include files, not directories.
        files = [f for f in all_items if os.path.isfile(os.path.join(DESKTOP_PATH, f))]
        
        # Exclude hidden files (like .DS_Store) and the log file itself.
        files_to_rename = [f for f in files if not f.startswith('.') and f != 'changes.log']

        if not files_to_rename:
            print("Pawku-chan found no files on the desktop to rename.")
            return

        # Choose a random file to be the victim.
        chosen_file = random.choice(files_to_rename)
        
        # Split the filename from its extension.
        file_name, file_ext = os.path.splitext(chosen_file)
        
        # Generate the new pretentious name.
        new_name = f"{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}{file_ext}"
        
        # Get the full old and new paths.
        original_path = os.path.join(DESKTOP_PATH, chosen_file)
        new_path = os.path.join(DESKTOP_PATH, new_name)
        
        # Ensure the new name doesn't already exist. If it does, just skip.
        if os.path.exists(new_path):
            print(f"Pawku-chan's chosen name '{new_name}' already exists. Skipping.")
            return

        # Perform the rename.
        os.rename(original_path, new_path)
        print(f"Renamed '{chosen_file}' to '{new_name}'")
        
        # Log the change so it can be undone.
        log_change(original_path, new_path)

    except FileNotFoundError:
        print(f"Error: Desktop path not found at {DESKTOP_PATH}")
    except Exception as e:
        print(f"An unexpected error occurred in rename_a_file: {e}")

if __name__ == '__main__':
    # This allows you to test the script directly.
    # Run 'python3 renamer.py' in your terminal.
    print("Testing the renamer module...")
    rename_a_file()
