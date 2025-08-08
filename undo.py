import os

# --- Configuration ---
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'changes.log')


def restore_desktop():
    """
    Restores the desktop to its initial state by:
    - Undoing file renames
    - Restoring deleted files from trash
    - Resetting icon positions (if logged)
    """
    print("Pawku-chan feels remorse. Attempting to restore your desktop...")
    if not os.path.exists(LOG_FILE_PATH):
        print("Log file not found. Nothing to undo!")
        return

    try:
        with open(LOG_FILE_PATH, 'r') as log_file:
            log_entries = log_file.readlines()
    except Exception as e:
        print(f"Error reading log file: {e}")
        return

    for entry in reversed(log_entries):
        entry = entry.strip()
        if not entry:
            continue
        # Handle deleted files
        if entry.startswith("DELETED,"):
            deleted_path = entry.split(',', 1)[1]
            filename = os.path.basename(deleted_path)
            trash_dir = os.path.expanduser('~/.local/share/Trash/files')
            trashed_file = os.path.join(trash_dir, filename)
            desktop_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
            restore_path = os.path.join(desktop_dir, filename)
            try:
                if os.path.exists(trashed_file):
                    os.rename(trashed_file, restore_path)
                    print(f"Restored deleted file: {filename}")
                else:
                    print(f"Could not find {filename} in trash.")
            except Exception as e:
                print(f"Error restoring deleted file {filename}: {e}")
            continue
        # Handle renames
        if ',' in entry:
            original_path, new_path = entry.split(',', 1)
            if os.path.exists(new_path):
                try:
                    os.rename(new_path, original_path)
                    print(f"Restored '{os.path.basename(new_path)}' to '{os.path.basename(original_path)}'")
                except Exception as e:
                    print(f"Error restoring rename {new_path} -> {original_path}: {e}")
            else:
                print(f"Warning: Could not find '{os.path.basename(new_path)}'. It may have been moved or deleted.")
            continue
        # Handle icon position resets (if you log them in the future)
        # Add logic here if you log icon positions

    # After undoing, clear the log file
    try:
        with open(LOG_FILE_PATH, 'w') as log_file:
            log_file.write("")
        print("\nUndo process complete. The log file has been cleared.")
    except Exception as e:
        print(f"Could not clear the log file: {e}")



if __name__ == '__main__':
    # This makes the script runnable from the command line.
    restore_desktop()
