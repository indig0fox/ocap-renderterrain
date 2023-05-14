import os
import subprocess


# define functions
# get list of folders in a directory
def get_folder_list(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

# get list of files in a directory
def get_file_list(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def get_metadata(path):
    # get metadata from worldname
    if not os.path.exists(path):
        return None
    with open(path) as f:
        metadata = f.read()
    return metadata

def convert_emf_to_png(in_file, out_file):
  # convert emf file to png
  from PIL import Image
  Image.MAX_IMAGE_PIXELS = None
  Image.open(in_file).save(out_file, 'PNG')


def convert_svg_to_png(in_file, out_file):
  # convert svg file to png
  import cairosvg
  cairosvg.svg2png(url=in_file, write_to=out_file)
  
  

