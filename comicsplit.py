import os
import numpy as np
from PIL import Image
import argparse

def process_image(image_path, output_path, tolerance):
    # Open the image in RGB mode and also create a grayscale copy for processing
    img = Image.open(image_path)
    img_gray = img.convert('L')
    img_array = np.array(img_gray)

    # Identify rows that are entirely white or black within the tolerance
    white_rows = np.all(img_array >= (255 - tolerance), axis=1)
    black_rows = np.all(img_array <= tolerance, axis=1)

    split_rows = white_rows | black_rows

    # Get indices of rows that mark the start or end of these segments
    indices = np.where(split_rows)[0]
    indices = np.concatenate(([0], indices, [img_array.shape[0] - 1]))

    # Split image
    img_array_color = np.array(img)
    split_images = []
    for i in range(len(indices) - 1):
        start = indices[i] + 1
        end = indices[i + 1]
        if start < end:
            split_images.append(img_array_color[start:end])

    # Saving split images
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    extension = os.path.splitext(image_path)[1]

    for idx, split_img in enumerate(split_images):
        split_output_path = os.path.join(output_path, f"{base_name}_sp_{idx + 1}{extension}")
        processed_img = Image.fromarray(split_img)
        
        # Convert image to RGB mode if it's not already
        if processed_img.mode != 'RGB':
            processed_img = processed_img.convert('RGB')
        
        os.makedirs(os.path.dirname(split_output_path), exist_ok=True)
        processed_img.save(split_output_path)
        print(f"Processed and saved: {split_output_path}")


def process_folder(input_folder, output_folder, tolerance):
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp','webp', 'gif')):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, input_folder)
                output_path = os.path.join(output_folder, os.path.dirname(relative_path))
                
                process_image(input_path, output_path, tolerance)

def main():
    parser = argparse.ArgumentParser(description="Horizantally split long comic images.")
    parser.add_argument('-i', '--input', type=str, required=True, help="Input folder containing images.")
    parser.add_argument('-o', '--output', type=str, required=True, help="Output folder for processed images.")
    parser.add_argument('-t', '--tolerance', type=int, default=10, help="Tolerance level (default: 10).")
    args = parser.parse_args()

    process_folder(args.input, args.output, args.tolerance)

if __name__ == "__main__":
    main()
