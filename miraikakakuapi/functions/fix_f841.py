#!/usr/bin/env python3
"""Fix F841 errors: Add logger.error() for unused exception variables"""

import re


def fix_f841_errors(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    # Line numbers where F841 errors occur (0-indexed)
    error_lines = [75, 84, 430, 563, 728, 953, 1609, 1815, 3218, 3301, 3406]

    for line_num in sorted(error_lines, reverse=True):
        if line_num < len(lines):
            line = lines[line_num]
            # Check if this is an except line with unused 'e'
            if "except Exception as e:" in line or "except" in line and "as e:" in line:
                # Find the indentation level
                indent = len(line) - len(line.lstrip())
                # Add logger.error() in the next line
                next_line_num = line_num + 1
                if next_line_num < len(lines):
                    next_line = lines[next_line_num]
                    # Check if next line is pass or empty
                    if "pass" in next_line or next_line.strip() == "":
                        # Replace with logger.error()
                        lines[next_line_num] = (
                            " " * (indent + 4)
                            + 'logger.error(f"Error occurred: {e}")\n'
                        )
                    elif "logger" not in next_line:
                        # Insert logger.error() before existing code
                        lines.insert(
                            next_line_num,
                            " " * (indent + 4)
                            + 'logger.error(f"Error occurred: {e}")\n',
                        )

    with open(filename, "w") as f:
        f.writelines(lines)

    print(f"Fixed F841 errors in {filename}")


if __name__ == "__main__":
    fix_f841_errors("production_main.py")
