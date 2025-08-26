#!/usr/bin/env python3
"""Fix E304 errors: Remove blank lines after function decorators"""

import re


def fix_e304_errors(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    fixed_lines = []
    i = 0
    while i < len(lines):
        fixed_lines.append(lines[i])
        # Check if current line is a decorator
        if lines[i].strip().startswith("@"):
            # Skip any blank lines after decorator
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            # If we skipped blank lines, continue from non-blank line
            if j > i + 1:
                i = j - 1
        i += 1

    with open(filename, "w") as f:
        f.writelines(fixed_lines)

    print(f"Fixed E304 errors in {filename}")


if __name__ == "__main__":
    fix_e304_errors("production_main.py")
