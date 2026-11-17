import os
from PIL import Image

TARGET_REF_PATH = r"C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\.user_uploaded\media_1794927072901_402b18d0.jpg"
NEW_EDITOR_PATH = r"C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\editor_stages_collapsed.png"
COMP_OUTPUT_PATH = r"C:\Users\CH SANDEEP\.gemini\antigravity\brain\e3539cfe-1379-4d58-868f-a3ad5b4c09bd\editor_stages_verification\comparison_editor_dropdown_stages.png"

def make_comparison():
    target_img = Image.open(TARGET_REF_PATH)
    editor_img = Image.open(NEW_EDITOR_PATH)

    # Let's resize target_img height to match editor_img height
    target_ratio = target_img.width / target_img.height
    new_target_height = editor_img.height
    new_target_width = int(new_target_height * target_ratio)
    target_resized = target_img.resize((new_target_width, new_target_height), Image.Resampling.LANCZOS)

    # Create composite
    total_width = new_target_width + editor_img.width
    comp_img = Image.new("RGB", (total_width, new_target_height), (240, 240, 240))
    comp_img.paste(target_resized, (0, 0))
    comp_img.paste(editor_img, (new_target_width, 0))

    comp_img.save(COMP_OUTPUT_PATH, quality=92)
    print(f"Composite saved to: {COMP_OUTPUT_PATH}")

if __name__ == "__main__":
    make_comparison()
