import os

file_path = 'app/routes/api.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Indices are 0-based.
# We want to remove lines 790 to 985 (1-based).
# This corresponds to indices 789 to 984.
# We keep 0 to 788 (lines 1 to 789).
# We keep 985 to end (lines 986 to end).

start_delete_idx = 789
end_delete_idx = 985 # Slice end is exclusive, so 985 means up to 984.

print(f"Total lines: {len(lines)}")
print(f"Line 789 (Keep): {lines[788]!r}")
print(f"Line 790 (Delete): {lines[789]!r}")
print(f"Line 985 (Delete): {lines[984]!r}")
print(f"Line 986 (Keep): {lines[985]!r}")

# Verify content looks like the duplicate block
if "add_to_wallet" in lines[791]: # Line 792
    print("Verified: Duplicate block start found.")
else:
    print("WARNING: Content mismatch at start of block.")

if "@api_bp.route('/user/profile'" in lines[985]: # Line 986
    print("Verified: Profile route found after block.")
else:
    print("WARNING: Content mismatch at end of block.")

new_lines = lines[:start_delete_idx] + lines[end_delete_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"New total lines: {len(new_lines)}")
print("File updated.")
