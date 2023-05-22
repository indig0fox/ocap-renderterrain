import os
import sys
import subprocess

# https://www.cyberciti.biz/faq/linux-unix-optimize-lossless-png-images-with-optipng-command/

def compress_images_in_folder(parent_path):
    """Recursively compresses all PNG files in a folder using ect."""
    if not os.path.exists(parent_path):
        print('Path does not exist:', parent_path)
        return
    print('Compressing files in path:', parent_path)

    # get all PNG files in parent_path, recursively
    png_files = []
    for root, dirs, files in os.walk(parent_path):
        for file in files:
            if file.endswith('.png'):
                png_files.append(os.path.join(root, file))

    optimization_level_preset = 1 # 0 to 7
    for file in png_files:
        subprocess.call(f'optipng -preserve -quiet {file}', shell=True)

def compress_single_image (path):
    """Apply compression optimization to a single image."""
    if not os.path.exists(path):
        print('Path does not exist:', path)
        return
    print('Compressing single file:', path)

    # compress the designated path
    optimization_level_preset = 1 # 0 to 7
    subprocess.call(f'optipng -preserve -o{optimization_level_preset} {path}', shell=True)