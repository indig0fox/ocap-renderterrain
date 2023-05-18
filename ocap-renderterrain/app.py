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

# for each folder in INPUT_FOLDER
for WORLDNAME_PATH in world_list:
    # define constants
    WORLDNAME = WORLDNAME_PATH.split("/")[-1]
    INPUT_FOLDER = f"./input/{WORLDNAME}"
    OUTPUT_FOLDER = f"./output/{WORLDNAME}"
    TEMP_FOLDER = f"./temp/{WORLDNAME}"

    print("PROCESSING", WORLDNAME)

    # delete everything in the temp and output folders wihtout deleting the folder itself
    for TGT_FOLDER in [OUTPUT_FOLDER, TEMP_FOLDER]:
        if not os.path.exists(TGT_FOLDER):
            os.makedirs(TGT_FOLDER)
        else:
            for filename in os.listdir(TGT_FOLDER):
                file_path = os.path.join(TGT_FOLDER, filename)
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

    # WORLD_JSON["imageSize"] = 16384
    WORLD_JSON["imageSize"] = WORLD_JSON["worldSize"]
    WORLD_JSON["multiplier"] = WORLD_JSON["imageSize"] / WORLD_JSON["worldSize"]

    # XYZ_FILE_PATH = os.path.join(INPUT_FOLDER, f"{WORLDNAME}.xyz")
    # if not os.path.exists(XYZ_FILE_PATH):
    #     print(f"No XYZ file found ({XYZ_FILE_PATH}), exiting...")
    #     sys.exit(1)

    ASC_FILE_PATH = os.path.join(INPUT_FOLDER, f"{WORLDNAME}.asc")
    if not os.path.exists(ASC_FILE_PATH):
        print(f"No ASC file found ({ASC_FILE_PATH}), exiting...")
        sys.exit(1)

    # show gdalinfo for ASC_FILE_PATH
    subprocess.call(f'gdalinfo -mm {ASC_FILE_PATH}', shell=True)

    SVG_FILE_PATH = os.path.join(INPUT_FOLDER, f"{WORLDNAME}.svg")
    if not os.path.exists(SVG_FILE_PATH):
        print(f"No EMF file found ({SVG_FILE_PATH}), exiting...")
        sys.exit(1)

    # SVG > PNG VARIABLES
    SVG_FILE_PROC_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}.svg")
    PNG_DEFAULT_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}.png")

    SVG_DARK_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_dark.svg")
    PNG_DARK_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_dark.png")

    ########################################

    SVG_LANDONLY_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_landonly.svg")
    PNG_LANDONLY_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_landonly.png")

    SVG_NOLAND_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_noland.svg")
    PNG_NOLAND_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_noland.png")

    ########################################

    PNG_HILLSHADE_BASE_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_landonly_hillshade.png")
    PNG_COLORRELIEF_BASE_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_landonly_colorrelief.png")

    ########################################

    PNG_TOPO_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_topo.png")
    PNG_TOPORELIEF_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_toporelief.png")
    PNG_COLORRELIEF_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_colorrelief.png")

    ########################################


    # first, preprocess the arma 3 svg as there are some things wrong with it
    print(f"=== Preprocessing SVG... {WORLDNAME} ===")
    file_conversion.preprocess_svg(SVG_FILE_PATH, SVG_FILE_PROC_PATH)

    # render alternates
    print(f"=== Generating \"dark\" svg... {WORLDNAME} ===")
    file_conversion.generate_svg_dark(SVG_FILE_PROC_PATH, SVG_DARK_FILE_PATH)
    print(f"=== Generating \"landonly\" svg... {WORLDNAME} ===")
    file_conversion.generate_svg_landonly(SVG_FILE_PROC_PATH, SVG_LANDONLY_FILE_PATH)
    print(f"=== Generating \"noland\" svg... {WORLDNAME} ===")
    file_conversion.generate_svg_noland(SVG_FILE_PROC_PATH, SVG_NOLAND_FILE_PATH)
    # print(f"=== Generating \"forestonly\" svg... {WORLDNAME} ===")
    # file_conversion.generate_svg_forestonly(SVG_FILE_PROC_PATH, SVG_FORESTONLY_FILE_PATH)

    ########################################

    # then, convert the svg to png. last param is the xy size of the png
    print(f"=== Generating default PNG... {WORLDNAME} ===")
    # do this in two steps - maps like Beketov break with how much scattered forest it has
    file_conversion.convert_svg_to_png(
        SVG_FILE_PROC_PATH,
        PNG_TOPO_FILE_PATH,
        WORLD_JSON.get("imageSize", 16384)
    )
    print(f"=== Generating \"dark\" PNG... {WORLDNAME} ===")
    file_conversion.convert_svg_to_png(
        SVG_DARK_FILE_PATH,
        PNG_DARK_FILE_PATH,
        WORLD_JSON.get("imageSize", 16384)
    )
    print(f"=== Generating landonly PNG... {WORLDNAME} ===")
    file_conversion.convert_svg_to_png(
        SVG_LANDONLY_FILE_PATH,
        PNG_LANDONLY_FILE_PATH,
        WORLD_JSON.get("imageSize", 16384),
    )
    print(f"=== Generating noland PNG... {WORLDNAME} ===")
    file_conversion.convert_svg_to_png(
        SVG_NOLAND_FILE_PATH,
        PNG_NOLAND_FILE_PATH,
        WORLD_JSON.get("imageSize", 16384),
    )
    # print(f"=== Generating forestonly PNG... {WORLDNAME} ===")
    # file_conversion.convert_svg_to_png(
    #     SVG_FORESTONLY_FILE_PATH,
    #     PNG_FORESTONLY_FILE_PATH,
    #     WORLD_JSON.get("imageSize", 16384),
    # )

    ########################################

    # get visual layers from dem
    HILLSHADE_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_hillshade_raw.png")
    HILLSHADE_HALFOPACITY_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_hillshade_halfopacity.png")
    COLORRELIEF_FILE_PATH = os.path.join(TEMP_FOLDER, f"{WORLDNAME}_colorrelief_raw.png")
    print(f"=== Generating hillshade and colorrelief... {WORLDNAME} ===")
    print("Generating colorrelief...")
    file_conversion.generate_colorrelief(
        ASC_FILE_PATH,
        PNG_COLORRELIEF_FILE_PATH,
        WORLD_JSON.get("imageSize", 16384)
    )
    print("Generating hillshade...")
    file_conversion.generate_heightmap(
        ASC_FILE_PATH,
        HILLSHADE_FILE_PATH,
        WORLD_JSON.get("imageSize", 16384)
    )
    print("Setting half opacity on hillshade for later application...")
    file_conversion.set_half_opacity(
        HILLSHADE_FILE_PATH,
        HILLSHADE_HALFOPACITY_FILE_PATH
    )

    ########################################

    # Now, we'll overlay the hillshade and colorrelief onto the landonly PNG and save each as a file
    print(f"=== Overlaying hillshade onto landonly PNG... {WORLDNAME} ===")

    # overlay hillshade onto landonly
    print("Processing hillshade...")
    file_conversion.multiply_images(
        os.path.abspath(PNG_LANDONLY_FILE_PATH),
        os.path.abspath(HILLSHADE_HALFOPACITY_FILE_PATH),
        os.path.abspath(PNG_HILLSHADE_BASE_FILE_PATH)
    )
    # We're going to skip any compositing of colorrelief here. We'll use that as its own base layer since we're more concerned about elevation representation.

    ########################################

    print(f"=== Adding features to PNG... {WORLDNAME} ===")
    # DARK is already ready
    # composite noland onto base images
    print(f"=== Compositing PNGs... {WORLDNAME} ===")
    print("Processing colorrelief...")
    file_conversion.composite_images(
        PNG_COLORRELIEF_FILE_PATH,
        PNG_NOLAND_FILE_PATH,
        PNG_COLORRELIEF_FILE_PATH
    )
    print("Processing hillshade...")
    file_conversion.composite_images(
        PNG_HILLSHADE_BASE_FILE_PATH,
        PNG_NOLAND_FILE_PATH,
        PNG_TOPORELIEF_FILE_PATH
    )

    ########################################

    for outfile in [
        PNG_TOPO_FILE_PATH,
        PNG_DARK_FILE_PATH,
        PNG_TOPORELIEF_FILE_PATH,
        PNG_COLORRELIEF_FILE_PATH,
    ]:
        print(f"=== Removing alpha channel from {outfile}... {WORLDNAME} ===")
        file_conversion.convert_png_to_24bit(outfile, outfile)
        print(f"=== Moving {outfile} to output folder... {WORLDNAME} ===")
        shutil.move(outfile, os.path.join(OUTPUT_FOLDER, os.path.basename(outfile)))

    # write metadata file
    print(f"=== Writing metadata file... {WORLDNAME} ===")
    WORLD_JSON["hasTopoDark"] = True
    WORLD_JSON["hasTopoRelief"] = True
    WORLD_JSON["hasColorRelief"] = True
    with open(os.path.join(OUTPUT_FOLDER, "map.json"), "w", encoding="utf-8") as outfile:
        json.dump(WORLD_JSON, outfile)
        outfile.close()

    print("=== Completed tasks for", WORLDNAME, "===")



print("Completed all tasks!")
input("Press Enter to continue...")
