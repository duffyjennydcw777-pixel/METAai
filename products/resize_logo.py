import os
from PIL import Image

def resize_to_3_1(input_path, output_path):
    print(f"Opening: {input_path}")
    if not os.path.exists(input_path):
        print("File not found!")
        return

    with Image.open(input_path) as img:
        width, height = img.size
        print(f"Original size: {width}x{height}")
        
        # Target aspect ratio is 3:1
        target_ratio = 3.0
        current_ratio = width / height
        
        if current_ratio > target_ratio:
            # Image is too wide, crop width
            new_width = int(height * target_ratio)
            left = (width - new_width) / 2
            right = (width + new_width) / 2
            top = 0
            bottom = height
        else:
            # Image is too tall, crop height
            new_height = int(width / target_ratio)
            left = 0
            right = width
            top = (height - new_height) / 2
            bottom = (height + new_height) / 2
            
        print(f"Cropping to: {right-left}x{bottom-top} (3:1 ratio)")
        img_cropped = img.crop((left, top, right, bottom))
        
        # Resize to standard 900x300 for good measure
        img_resized = img_cropped.resize((900, 300), Image.Resampling.LANCZOS)
        img_resized.save(output_path)
        print(f"Saved exact 3:1 image to: {output_path}")

input_img = r"C:\Users\Gigabyte\.gemini\antigravity\brain\cc47b841-6fca-46e0-b537-47ccc30a7b97\solocto_logo_1778246556577.png"
output_img = r"C:\Users\Gigabyte\.gemini\antigravity\brain\cc47b841-6fca-46e0-b537-47ccc30a7b97\solocto_logo_3x1_exact.png"

resize_to_3_1(input_img, output_img)
