import os
import re
import argparse
import sys

def sanitize_ntfs_names(root_dir=None, dry_run=False, max_length=255):
    """
    Sanitize filenames to be NTFS-compliant.

    Args:
        root_dir: Directory to process (default: current directory)
        dry_run: If True, only show what would be changed
        max_length: Maximum allowed filename length (NTFS limit)
    """
    # NTFS forbidden characters: < > : " / \ | ? * and control characters
    # Also avoid trailing spaces/dots which Windows strips
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1f]'

    if root_dir is None:
        root_dir = os.getcwd()

    # Validate root directory exists
    if not os.path.exists(root_dir):
        print(f"Error: Directory '{root_dir}' does not exist.")
        return

    change_count = 0
    skipped_count = 0
    error_count = 0

    print(f"--- Starting NTFS Sanitization ---")
    print(f"Directory: {root_dir}")
    print(f"Dry run: {dry_run}")
    print("-" * 50)

    # topdown=False ensures we rename children before parents
    for root, dirs, files in os.walk(root_dir, topdown=False):
        for name in dirs + files:
            # Skip the script itself and hidden system files
            if name == os.path.basename(__file__):
                continue

            old_path = os.path.join(root, name)

            # Check if path is too long for NTFS
            if len(os.path.basename(old_path)) > max_length:
                print(f"[WARNING] Name too long ({len(name)} chars): {name[:50]}...")
                skipped_count += 1
                continue

            # Check for invalid characters
            has_invalid = re.search(forbidden_chars, name)

            # Check for trailing spaces or dots (Windows strips these)
            has_trailing = name.strip(' .') != name

            # Check for reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
            reserved_pattern = r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?$'
            is_reserved = re.match(reserved_pattern, name, re.IGNORECASE)

            if has_invalid or has_trailing or is_reserved:
                # Start with original name
                new_name = name

                # Replace invalid characters
                if has_invalid:
                    new_name = re.sub(forbidden_chars, '_', new_name)

                # Remove trailing spaces and dots
                if has_trailing:
                    new_name = new_name.strip(' .')
                    # Ensure we don't create an empty name
                    if not new_name:
                        new_name = "unnamed"

                # Handle reserved names
                if is_reserved:
                    new_name = "_" + new_name

                # Ensure length doesn't exceed limit after modifications
                if len(new_name) > max_length:
                    base, ext = os.path.splitext(new_name)
                    # Truncate base name, keep extension
                    truncate_length = max_length - len(ext)
                    new_name = base[:truncate_length] + ext

                new_path = os.path.join(root, new_name)

                # Collision handling
                counter = 1
                base, ext = os.path.splitext(new_path)
                while os.path.exists(new_path):
                    new_name = f"{os.path.splitext(new_name)[0]}_{counter}{ext}"
                    new_path = os.path.join(root, new_name)
                    counter += 1

                # Skip if no actual change needed
                if new_name == name:
                    continue

                try:
                    relative_path = os.path.relpath(root, root_dir)

                    if dry_run:
                        print(f"[WOULD CHANGE]")
                    else:
                        print(f"[CHANGED]")

                    print(f"  Location: ./{relative_path if relative_path != '.' else ''}")
                    print(f"  Original: {name}")
                    print(f"  Modified: {new_name}")

                    if has_invalid:
                        print(f"  Reason: Contains invalid NTFS characters")
                    if has_trailing:
                        print(f"  Reason: Trailing spaces/dots")
                    if is_reserved:
                        print(f"  Reason: Reserved Windows name")

                    print("-" * 30)

                    if not dry_run:
                        os.rename(old_path, new_path)

                    change_count += 1

                except OSError as e:
                    print(f"[ERROR] Could not rename '{name}': {e}")
                    error_count += 1
                except Exception as e:
                    print(f"[UNEXPECTED ERROR] Processing '{name}': {e}")
                    error_count += 1

    print(f"\n--- Process Complete ---")
    print(f"Total renamed: {change_count}")
    print(f"Skipped (too long): {skipped_count}")
    print(f"Errors: {error_count}")

    if dry_run:
        print("\nNote: This was a dry run. No files were actually changed.")
        print("Run without --dry-run to apply changes.")

def main():
    parser = argparse.ArgumentParser(
        description='Sanitize filenames to be NTFS-compliant.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Process current directory
  %(prog)s /path/to/folder     # Process specific directory
  %(prog)s --dry-run           # Show what would be changed
  %(prog)s --max-length 100    # Set custom max filename length
        """
    )

    parser.add_argument('directory', nargs='?', default=None,
                       help='Directory to process (default: current directory)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without actually renaming')
    parser.add_argument('--max-length', type=int, default=255,
                       help='Maximum filename length (default: 255)')

    args = parser.parse_args()

    try:
        sanitize_ntfs_names(
            root_dir=args.directory,
            dry_run=args.dry_run,
            max_length=args.max_length
        )
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
