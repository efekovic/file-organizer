import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

# File extension mapping
DIRECTORIES = {
    "HTML": [".html5", ".html", ".htm", ".xhtml"],
    "IMAGES": [".jpeg", ".jpg", ".tiff", ".gif", ".bmp", ".png", ".bpg", ".svg", ".heif", ".psd"],
    "VIDEOS": [".avi", ".flv", ".wmv", ".mov", ".mp4", ".webm", ".vob", ".mng", ".qt", ".mpg", ".mpeg", ".m4v"],
    "DOCUMENTS": [".oxps", ".epub", ".pages", ".docx", ".doc", ".fdf", ".ods", ".odt", ".pwi", ".xsn", ".xltx", ".xlsb", ".xlsx", ".csv", ".pdf", ".txt"],
    "ARCHIVES": [".a", ".ar", ".cpio", ".iso", ".tar", ".gz", ".rz", ".7z", ".dmg", ".rar", ".xar", ".zip"],
    "AUDIO": [".aac", ".aa", ".dvf", ".m4a", ".m4b", ".m4p", ".mp3", ".msv", ".ogg", ".oga", ".raw", ".vox", ".wav", ".wma"],
}

def setup_logging(folder_path: Path):
    """
    Configures logging to write to a file named 'file_organizer.log' 
    inside the target directory.
    """
    log_file = folder_path / 'file_organizer.log'
    
    logging.basicConfig(
        filename=str(log_file),
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True
    )

def organize_directory(path_str: str, dry_run: bool = False):
    """
    Scans the directory and moves files into subfolders based on extensions.
    """
    parent_dir = Path(path_str)

    # Validation
    if not parent_dir.exists():
        print(f"Error: The path '{path_str}' does not exist.")
        return
    if not parent_dir.is_dir():
        print(f"Error: The path '{path_str}' is not a directory.")
        return

    # Setup logging now that we know the path is valid
    setup_logging(parent_dir)
    
    mode = "DRY RUN" if dry_run else "ACTUAL RUN"
    logging.info(f"--- Starting cleanup ({mode}) in: {path_str} ---")
    print(f"Organizing files in: {path_str}... ({mode})")

    # Track statistics
    stats = {category: 0 for category in DIRECTORIES.keys()}
    stats["OTHER"] = 0
    files_processed = 0

    for item in parent_dir.iterdir():
        # Skip directories and the log file itself
        if item.is_dir() or item.name == 'file_organizer.log':
            continue

        file_type = item.suffix.lower()
        moved = False

        try:
            for category, extensions in DIRECTORIES.items():
                if file_type in extensions:
                    dest_dir = parent_dir / category
                    
                    if not dry_run:
                        dest_dir.mkdir(exist_ok=True)
                    
                    # Handle file name conflicts
                    dest_path = dest_dir / item.name
                    if dest_path.exists():
                        stem = item.stem
                        suffix = item.suffix
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dest_path = dest_dir / f"{stem}_{timestamp}{suffix}"
                        logging.warning(f"File exists, renaming: {item.name} -> {dest_path.name}")
                    
                    # Move the file or simulate move
                    if dry_run:
                        print(f"Would move: {item.name} -> {category}")
                        logging.info(f"DRY RUN: {item.name} -> {category}")
                    else:
                        shutil.move(str(item), str(dest_path))
                        logging.info(f"MOVED: {item.name} -> {category}")
                    
                    stats[category] += 1
                    files_processed += 1
                    moved = True
                    break
            
            # If no category matched, move to OTHER
            if not moved:
                other_dir = parent_dir / "OTHER"
                
                if not dry_run:
                    other_dir.mkdir(exist_ok=True)
                
                dest_path = other_dir / item.name
                if dest_path.exists():
                    stem = item.stem
                    suffix = item.suffix
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_path = other_dir / f"{stem}_{timestamp}{suffix}"
                    logging.warning(f"File exists, renaming: {item.name} -> {dest_path.name}")
                
                if dry_run:
                    print(f"Would move: {item.name} -> OTHER")
                    logging.warning(f"DRY RUN UNKNOWN: {item.name} -> OTHER")
                else:
                    shutil.move(str(item), str(dest_path))
                    logging.warning(f"UNKNOWN: {item.name} -> OTHER")
                
                stats["OTHER"] += 1
                files_processed += 1

        except shutil.Error as e:
            logging.error(f"ERROR moving {item.name}: {e}")
            print(f"Error moving {item.name}: {e}")
        except Exception as e:
            logging.error(f"UNEXPECTED ERROR with {item.name}: {e}")
            print(f"Unexpected error with {item.name}: {e}")

    # Print summary
    logging.info("--- Summary ---")
    print("\n" + "="*50)
    print("ORGANIZATION SUMMARY")
    print("="*50)
    print(f"Total files processed: {files_processed}")
    print("-"*50)
    
    for category, count in stats.items():
        if count > 0:
            print(f"{category}: {count} file(s)")
            logging.info(f"SUMMARY: {category}: {count} file(s)")
    
    print("="*50)
    
    logging.info("--- Cleanup Finished ---")
    print(f"\nOrganization complete. Check '{parent_dir / 'file_organizer.log'}' for details.")

if __name__ == "__main__":
    # Get path from user input
    target_path = input("Enter the path of the folder you want to organize: ").strip()
    
    # Remove quotes if the user copied "C:\Path" with quotes
    target_path = target_path.strip('"').strip("'")
    
    # Handle empty input
    if not target_path:
        print("Error: No path provided.")
        exit(1)
    
    # Ask if user wants dry run
    dry_run_input = input("Do you want to do a dry run first? (y/n): ").strip().lower()
    dry_run = dry_run_input == 'y'
    
    organize_directory(target_path, dry_run)
    
    # If it was a dry run, ask if they want to proceed
    if dry_run:
        proceed = input("\nDo you want to proceed with actual organization? (y/n): ").strip().lower()
        if proceed == 'y':
            organize_directory(target_path, dry_run=False)
        else:
            print("Organization cancelled.")