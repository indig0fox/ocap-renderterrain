import os
import shutil
import sys
import subprocess
from time import sleep

import shapely
import json
import numpy as np
import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt

# import modules from ./modules
from modules import file_conversion


# remove all imagemagick file limits
subprocess.call("magick policy none", shell=True)

# print a list of files in .
print("Files in .:")
for f in os.listdir("."):
    print(f)

# get list of folders in input folder
world_list = [
    f for f in os.listdir("./input") if os.path.isdir(os.path.join("./input", f))
]

print("")
print("Found the following worlds:")
for world in world_list:
    print("", world)
print("")

input()

# for each folder in INPUT_FOLDER
for WORLDNAME_PATH in world_list:
    # define constants
    WORLDNAME = WORLDNAME_PATH.split("/")[-1]
    INPUT_FOLDER = f"./input/{WORLDNAME}"
    OUTPUT_FOLDER = f"./output/{WORLDNAME}"
    TEMP_FOLDER = f"./temp/{WORLDNAME}"

    print("PROCESSING", WORLDNAME)

    # delete everything in the temp folder wihtout deleting the folder itself
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)
    else:
        for filename in os.listdir(TEMP_FOLDER):
            file_path = os.path.join(TEMP_FOLDER, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                try:
                    os.unlink(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
            elif os.path.isdir(file_path):
                try:
                    shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

    # get metadata json
    WORLD_JSON_FILE_PATH = os.path.join(INPUT_FOLDER, "map.json")
    try:
        with open(WORLD_JSON_FILE_PATH, "r", encoding="utf-8") as infile:
            WORLD_JSON = json.load(infile)
            infile.close()
    except FileNotFoundError:
        print(f"No metadata file found ({WORLD_JSON_FILE_PATH}), exiting...")
        sys.exit(1)

    # XYZ_FILE_PATH = os.path.join(INPUT_FOLDER, f"{WORLDNAME}.xyz")
    # if not os.path.exists(XYZ_FILE_PATH):
    #     print(f"No XYZ file found ({XYZ_FILE_PATH}), exiting...")
    #     sys.exit(1)

    ASC_FILE_PATH = os.path.join(INPUT_FOLDER, f"{WORLDNAME}.asc")
    if not os.path.exists(ASC_FILE_PATH):
        print(f"No ASC file found ({ASC_FILE_PATH}), exiting...")
        sys.exit(1)

    SVG_FILE_PATH = os.path.join(INPUT_FOLDER, f"{WORLDNAME}.svg")
    if not os.path.exists(SVG_FILE_PATH):
        print(f"No EMF file found ({SVG_FILE_PATH}), exiting...")
        sys.exit(1)

    # SVG > PNG VARIABLES
    SVG_FILE_PROC_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}.svg")
    SVG_DARK_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_dark.svg")

    PNG_DEFAULT_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}.png")
    PNG_DARK_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_dark.png")

    # first, preprocess the arma 3 svg as there are some things wrong with it
    file_conversion.preprocess_svg(SVG_FILE_PATH, SVG_FILE_PROC_PATH)

    # render alternates
    file_conversion.generate_svg_dark(SVG_FILE_PROC_PATH, SVG_DARK_FILE_PATH)

    # then, convert the svg to png. last param is the xy size of the png
    file_conversion.convert_svg_to_24bit_png(
        SVG_FILE_PROC_PATH, PNG_DEFAULT_FILE_PATH, WORLD_JSON.get("imageSize", 16384)
    )
    file_conversion.convert_svg_to_24bit_png(
        SVG_DARK_FILE_PATH, PNG_DARK_FILE_PATH, WORLD_JSON.get("imageSize", 16384)
    )

    # get visual layers from dem
    HILLSHADE_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_hillshade.png")
    COLORRELIEF_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_colorrelief.png")
    file_conversion.generate_heightmap(ASC_FILE_PATH, HILLSHADE_FILE_PATH)
    file_conversion.generate_colorrelief(ASC_FILE_PATH, COLORRELIEF_FILE_PATH)


print("Completed all tasks!")