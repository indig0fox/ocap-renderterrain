import os
import shutil
import sys
import subprocess
import re
import json
from threading import Thread

# import modules from ./modules
from modules import file_conversion
from modules import compress

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


# Manual compression on-demand
# OUTPUT_FOLDER = "./output/csj_lowlands"
# WORLDNAME = "csj_lowlands"
# MAX_ZOOM = 6
# print(f"=== Compressing images... {WORLDNAME} ===")
# for zoom in range(0, MAX_ZOOM + 1):
#     print(f"Starting threads for compressing zoom level {zoom}...")
#     topo_compression = Thread(
#       target=compress.compress_images_in_folder,
#       args=(os.path.join(OUTPUT_FOLDER, str(zoom)),)
#     )
#     topoDark_compression = Thread(
#       target=compress.compress_images_in_folder,
#       args=(os.path.join(OUTPUT_FOLDER, "topoDark", str(zoom)),)
#     )
#     topoRelief_compression = Thread(
#       target=compress.compress_images_in_folder,
#       args=(os.path.join(OUTPUT_FOLDER, "topoRelief", str(zoom)),)
#     )
#     colorRelief_compression = Thread(
#       target=compress.compress_images_in_folder,
#       args=(os.path.join(OUTPUT_FOLDER, "colorRelief", str(zoom)),)
#     )
#     topo_compression.start()
#     topoDark_compression.start()
#     topoRelief_compression.start()
#     colorRelief_compression.start()
#     print("Waiting for threads to finish...")
#     topo_compression.join()
#     print(f"Topo compression finished (z{zoom}/{MAX_ZOOM}) (process 1/4)")
#     topoDark_compression.join()
#     print(f"TopoDark compression finished (z{zoom}/{MAX_ZOOM}) (process 2/4)")
#     topoRelief_compression.join()
#     print(f"TopoRelief compression finished (z{zoom}/{MAX_ZOOM}) (process 3/4)")
#     colorRelief_compression.join()
#     print(f"ColorRelief compression finished (z{zoom}/{MAX_ZOOM}) (process 4/4)")
# sys.exit(0)

# clear everything in TEMP_FOLDER
TEMP_FOLDER = "./temp"
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

#######################################

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
    file_conversion.multiply_images(
        os.path.abspath(PNG_LANDONLY_FILE_PATH),
        os.path.abspath(HILLSHADE_HALFOPACITY_FILE_PATH),
        os.path.abspath(PNG_HILLSHADE_BASE_FILE_PATH)
    )
    print(f"=== Overlaying hillshade onto colorrelief PNG... {WORLDNAME} ===")
    # overlay hillshade onto colorrelief
    file_conversion.multiply_images(
        os.path.abspath(PNG_COLORRELIEF_FILE_PATH),
        os.path.abspath(HILLSHADE_HALFOPACITY_FILE_PATH),
        os.path.abspath(PNG_COLORRELIEF_FILE_PATH)
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
        # print(f"=== Moving {outfile} to output folder... {WORLDNAME} ===")
        # shutil.move(outfile, os.path.join(OUTPUT_FOLDER, os.path.basename(outfile)))

    # generate tilesets
    print(f"=== Generating tilesets... {WORLDNAME} ===")
    # render topo to folder root
    print("Generating tileset \"topo\" to subfolder...")
    subprocess.call(
        f"gdal2tiles.py -p raster --xyz -z 0-8 -w all -r lanczos -t {WORLDNAME}_topo {PNG_TOPO_FILE_PATH} {OUTPUT_FOLDER}",
        shell=True,
    )
    # render dark, topo, and colorrelief to subfolders
    for outfile in [
        [PNG_DARK_FILE_PATH, "topoDark"],
        [PNG_TOPORELIEF_FILE_PATH, "topoRelief"],
        [PNG_COLORRELIEF_FILE_PATH, "colorRelief"],
    ]:
        image_path, folder_name = outfile
        print(f"Generating tileset \"{folder_name}\" to subfolder...")
        subprocess.call(
            f"gdal2tiles.py -p raster --xyz -z 0-8 -r lanczos -t {WORLDNAME}_{folder_name} {image_path} {os.path.join(OUTPUT_FOLDER, folder_name)}",
            shell=True,
        )

    # we need to check the max zoom that was rendered. the auto-clamped max zoom will vary based on original image size, which here is paired to the worldSize in m. we'll then update the metadata with the maxZoom.
    print(f"=== Updating metadata... {WORLDNAME} ===")
    MAX_ZOOM = 0
    # get files in output folder
    for filename in os.listdir(OUTPUT_FOLDER):
        # if filename is a one or two digit number, it's a zoom level
        if re.match(r"^\d{1,2}$", filename):
            # if the filename is a number, check if it's greater than max_zoom
            if int(filename) > MAX_ZOOM:
                MAX_ZOOM = int(filename)
    # update metadata
    WORLD_JSON["maxZoom"] = MAX_ZOOM

    # write metadata file
    print(f"=== Writing metadata file... {WORLDNAME} ===")
    WORLD_JSON["hasTopoDark"] = True
    WORLD_JSON["hasTopoRelief"] = True
    WORLD_JSON["hasColorRelief"] = True
    with open(os.path.join(OUTPUT_FOLDER, "map.json"), "w", encoding="utf-8") as outfile:
        json.dump(WORLD_JSON, outfile, indent=2)
        outfile.close()

    # render a georeferenced GeoTIFF of topoRelief and colorRelief
    print(f"=== Generating GeoTIFFs... {WORLDNAME} ===")
    # get bounds from metadata (worldsize)
    terrain_bounds = [
        [0, WORLD_JSON["worldSize"]],
        [WORLD_JSON["worldSize"], WORLD_JSON["worldSize"]],
        [WORLD_JSON["worldSize"], 0],
        [0, 0],
    ]
    # convert to geotiff
    print("Converting topoRelief to GeoTiff...")
    subprocess.call(
        f"gdal_translate -of GTiff -a_srs EPSG:3857 -a_ullr {terrain_bounds[0][0]} {terrain_bounds[0][1]} {terrain_bounds[2][0]} {terrain_bounds[2][1]} -co COMPRESS=DEFLATE {PNG_TOPORELIEF_FILE_PATH} {os.path.join(OUTPUT_FOLDER, f'{WORLDNAME}_topoRelief.tif')}",
        shell=True,)
    print("Converting colorRelief to GeoTiff...")
    subprocess.call(
        f"gdal_translate -of GTiff -a_srs EPSG:3857 -a_ullr {terrain_bounds[0][0]} {terrain_bounds[0][1]} {terrain_bounds[2][0]} {terrain_bounds[2][1]} -co COMPRESS=DEFLATE {PNG_COLORRELIEF_FILE_PATH} {os.path.join(OUTPUT_FOLDER, f'{WORLDNAME}_colorRelief.tif')}",
        shell=True,)

    
    # # generate a geojson of a 100m grid from 0 to 40km
    # print(f"=== Generating 40x40km geojson grid... {WORLDNAME} ===")
    # geojson_grid = {}
    # geojson_grid["type"] = "FeatureCollection"
    # geojson_grid["features"] = []
    # for x in range(0, 40001, 100):
    #     geojson_grid["features"].append({
    #         "type": "Feature",
    #         "properties": {
    #             "name": "grid",
    #             "stroke": "#555555",
    #             "stroke-width": 1,
    #             "stroke-opacity": 0.5,
    #             "gridlabel": x
    #         },
    #         "geometry": {
    #             "type": "LineString",
    #             "coordinates": [
    #                 [x, 0],
    #                 [x, 40000]
    #             ]
    #         },
    #     })
    # for y in range(0, 40001, 100):
    #     geojson_grid["features"].append({
    #         "type": "Feature",
    #         "properties": {
    #             "name": "grid",
    #             "stroke": "#555555",
    #             "stroke-width": 1,
    #             "stroke-opacity": 0.5,
    #             "gridlabel": y
    #         },
    #         "geometry": {
    #             "type": "LineString",
    #             "coordinates": [
    #                 [0, y],
    #                 [40000, y]
    #             ]
    #         },
    #     })

    # with open(os.path.join(OUTPUT_FOLDER, f"{WORLDNAME}_grid_unprojected.geojson"), "w", encoding="utf-8") as outfile:
    #     json.dump(geojson_grid, outfile)
    #     outfile.close()

    # # use gdal_translate to place it in EPSG:3857
    # print("Converting grid to EPSG:3857...")
    # subprocess.call(
    #     f"ogr2ogr -f \"GeoJSON\" -s_srs \"EPSG:3857\" -t_srs \"EPSG:4326\" {os.path.join(OUTPUT_FOLDER, f'{WORLDNAME}_grid.geojson')} {os.path.join(OUTPUT_FOLDER, f'{WORLDNAME}_grid_unprojected.geojson')}",
    #     shell=True,)
    


    


    # open threads for tiling
    print(f"=== Compressing images... {WORLDNAME} ===")
    for zoom in range(0, MAX_ZOOM + 1):
        print(f"Starting threads for compressing zoom level {zoom}...")
        topo_compression = Thread(
          target=compress.compress_images_in_folder,
          args=(os.path.join(OUTPUT_FOLDER, str(zoom)),)
        )
        topoDark_compression = Thread(
          target=compress.compress_images_in_folder,
          args=(os.path.join(OUTPUT_FOLDER, "topoDark", str(zoom)),)
        )
        topoRelief_compression = Thread(
          target=compress.compress_images_in_folder,
          args=(os.path.join(OUTPUT_FOLDER, "topoRelief", str(zoom)),)
        )
        colorRelief_compression = Thread(
          target=compress.compress_images_in_folder,
          args=(os.path.join(OUTPUT_FOLDER, "colorRelief", str(zoom)),)
        )
        topo_compression.start()
        topoDark_compression.start()
        topoRelief_compression.start()
        colorRelief_compression.start()
        topo_compression.join()
        print(f"Topo compression finished (z{zoom}/{MAX_ZOOM}) (process 1/4)")
        topoDark_compression.join()
        print(f"TopoDark compression finished (z{zoom}/{MAX_ZOOM}) (process 2/4)")
        topoRelief_compression.join()
        print(f"TopoRelief compression finished (z{zoom}/{MAX_ZOOM}) (process 3/4)")
        colorRelief_compression.join()
        print(f"ColorRelief compression finished (z{zoom}/{MAX_ZOOM}) (process 4/4)")


    

    print("=== Completed tasks for", WORLDNAME, "===")



print("Completed all tasks!")
input("Press Enter to continue...")
