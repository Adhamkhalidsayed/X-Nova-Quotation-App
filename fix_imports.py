with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "is_dark_mode = False" in line and i == 560:
        new_lines.append("import subprocess\n")
    new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)
