import os

# --- Configuration ---
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'changes.log')

def undo_renames():
    """
    Reads the log file in reverse and renames files back to their original names.
    """
    print("Pawku-chan feels remorse. Attempting to undo the 'improvements'...")
    
    if not os.path.exists(LOG_FILE_PATH):
        print("Log file not found. Nothing to undo!")
        return

    try:
        with open(LOG_FILE_PATH, 'r') as log_file:
            # Read all lines from the log file into a list.
            log_entries = log_file.readlines()
    except Exception as e:
        print(f"Error reading log file: {e}")
        return

    # We iterate through the log entries in reverse order (from last change to first).
    # This handles cases where a file might have been renamed multiple times.
    for entry in reversed(log_entries):
        entry = entry.strip()
        if not entry:
            continue

        try:
            original_path, new_path = entry.split(',')
            
            # Check if the "new" (currently named) file exists.
            if os.path.exists(new_path):
                # Rename it back to the original.
                os.rename(new_path, original_path)
                print(f"Restored '{os.path.basename(new_path)}' to '{os.path.basename(original_path)}'")
            else:
                print(f"Warning: Could not find '{os.path.basename(new_path)}'. It may have been moved or deleted.")

        except ValueError:
            print(f"Warning: Skipping malformed log entry: {entry}")
        except Exception as e:
            print(f"Error processing entry '{entry}': {e}")

    # After undoing, we can clear the log file so it doesn't run again.
    try:
        with open(LOG_FILE_PATH, 'w') as log_file:
            log_file.write("") # Overwrite with an empty string.
        print("\nUndo process complete. The log file has been cleared.")
    except Exception as e:
        print(f"Could not clear the log file: {e}")


if __name__ == '__main__':
    # This makes the script runnable from the command line.
    undo_renames()
