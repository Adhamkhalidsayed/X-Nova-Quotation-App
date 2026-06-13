import json
import os

with open("/Users/adhamkhalid/.gemini/antigravity/brain/6788afb1-cc79-4186-bcdd-3b8c44dd9113/.system_generated/logs/overview.txt", "r") as f:
    lines = f.readlines()

for line in reversed(lines):
    if "Showing lines 1 to" in line and "app.py" in line:
        print("Found a view_file output!")
        break

# Better: parse the json lines in overview.txt
for line in reversed(lines):
    try:
        data = json.loads(line)
        if data.get("type") == "TOOL_RESPONSE" and data.get("tool_calls"):
            for call in data["tool_calls"]:
                if call.get("name") == "view_file":
                    output = call.get("response", {}).get("output", "")
                    if "File Path: `file:///Users/adhamkhalid/Desktop/Quotation_App/app.py`" in output:
                        print("Found view_file response")
                        # extract lines
                        if "Showing lines 1 to 800" in output:
                            with open("recovered_1_800.txt", "w") as out:
                                out.write(output)
                                print("Wrote recovered_1_800.txt")
                        elif "Showing lines 794 to 900" in output:
                            with open("recovered_794_900.txt", "w") as out:
                                out.write(output)
                                print("Wrote recovered_794_900.txt")
    except:
        pass
