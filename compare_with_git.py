#!/usr/bin/python3
import subprocess
import os
from PIL import Image, ImageChops
import io
import imghdr
import numpy as np

# Define the brightness threshold (in percent)
# if no diff pixel is brighter than this consider files equal
BRIGHTNESS_THRESHOLD = 10

def compare_images():
    # Get the path of the repository
    repo_path = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).strip().decode('utf-8')
    # Get the list of changed files
    changed_files = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD']).strip().decode('utf-8').split('\n')
    for rel_path in changed_files:
        # Get the absolute path of the image
        image_path = os.path.join(repo_path, rel_path)
        # Check if the file exists
        if not os.path.exists(image_path):
            continue
        # Check if the file is an image
        if imghdr.what(image_path) is None:
            continue
        # Get the latest commit hash
        latest_commit = subprocess.check_output(['git', 'rev-list', '-1', 'HEAD', rel_path]).strip().decode('utf-8')
        # Get the image from the latest commit
        old_image_data = subprocess.check_output(['git', 'show', f'{latest_commit}:{rel_path}'])
        old_image = Image.open(io.BytesIO(old_image_data))
        # Convert to RGB
        old_image = old_image.convert('RGB')
        # Resize the image
        old_image = old_image.resize((128, 128))
        # Open the current version of the image
        current_image = Image.open(image_path)
        # Convert to RGB
        current_image = current_image.convert('RGB')
        # Resize the image
        current_image = current_image.resize((128, 128))
        # Create a diff image
        diff_image = ImageChops.difference(current_image, old_image)
        # Convert to luminance
        diff_image = diff_image.convert('L')
        # Convert to numpy array and check if any pixel is brighter than the threshold
        diff_array = np.array(diff_image)
        threshold = int(255 * BRIGHTNESS_THRESHOLD / 100)
        if (diff_array > threshold).any():
            # Save the diff image
            diff_image.save(f'{rel_path}#diff.png')
        else:
            # Check if the dimensions of the current image are smaller or equal to those of the old image
            if current_image.width <= old_image.width and current_image.height <= old_image.height:
                # Revert to unmodified version of the file
                with open(image_path, 'wb') as f:
                    f.write(old_image_data)

compare_images()