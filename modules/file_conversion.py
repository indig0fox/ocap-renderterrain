import os
import subprocess
import sys

import xml.etree.ElementTree as ET


def get_svg_items(root, category_id, item_type):
    """Get SVG items of a specific type from a specific category"""
    for category in root.findall("./{http://www.w3.org/2000/svg}g"):
        if category.get("id") == category_id:
            return category.findall("./{http://www.w3.org/2000/svg}" + item_type)


def preprocess_svg(in_file, out_file):
    """Preprocess SVG file"""

    """
    Some issues face us with the default SVG exports from Arma 3:
      1. There is no "fill=none" attribute on the
        <g id="countLines">
          <polyline>...</polyline>
        </g>
        element, so the lines are filled with black.
      2. The <ellipse> elements representing trees have no on-element fill or stroke attributes, so they're translated to black opaque circles. We also want to shrink the trees by 50% (to 6px radius) and add a stroke to them.
      3. There is no "fill=none" attribute on the
        <g id="roads">
          <polyline>...</polyline>
        </g>
        element, so the lines are filled with black.
      4. We want the text for mountains and location names to be 12px Arial.
      5. We want to set "fill=none" on airport polylines
    """

    # read in_file
    # with open(in_file, "r", encoding="utf-8") as f:
    #     svg = f.read()
    #     f.close()

    # read SVG as XML for parsing
    print("Reading SVG...")
    svg = ET.parse(in_file)
    svg_root = svg.getroot()
    if svg_root is None:
        print(f"Failed to parse SVG file ({in_file}), exiting...")
        sys.exit(1)

    print("Processing countLines...")
    # get all polylines under <g id="countLines">
    count_lines = get_svg_items(svg_root, "countLines", "polyline")

    # add fill=none to all polylines under <g id="countLines">
    for polyline in count_lines:
        polyline.set("fill", "none")

    print("Processing trees...")
    # get all ellipses under <g id="objects">
    objects_ellipses = get_svg_items(svg_root, "objects", "ellipse")

    # for all ellipses under <g id="objects">:
    # add fill=none
    # add stroke="url(#colorForestBorder)"
    for ellipse in objects_ellipses:
        ellipse.set("fill", "none")
        ellipse.set("stroke", "url(#colorForestBorder)")
        ellipse.set("rx", "6.00")
        ellipse.set("ry", "6.00")

    print("Processing roads...")
    # get all polylines under <g id="roads">
    roads_polylines = get_svg_items(svg_root, "roads", "polyline")

    # add fill=none to all polylines under <g id="roads">
    for polyline in roads_polylines:
        polyline.set("fill", "none")

    print("Processing mountains...")
    # get all text under <g id="mountains">
    mountains_text = get_svg_items(svg_root, "mountains", "text")

    # for all text under <g id="mountains">, set font-size to 10px and font-family to Arial
    for text in mountains_text:
        text.set("font-size", "10px")
        text.set("font-family", "Arial")

    print("Processing townNames...")
    # get all text under <g id="townNames">
    town_names_text = get_svg_items(svg_root, "townNames", "text")

    # for all text under <g id="townNames">, set font-size to 24px and font-family to Arial
    for text in town_names_text:
        text.set("font-size", "24px")
        text.set("font-family", "Arial")

    print("Processing airports...")
    # get all polylines under <g id="airports">
    airports_polylines = get_svg_items(svg_root, "airports", "polyline")

    # add fill=none to all polylines under <g id="airports">
    for polyline in airports_polylines:
        polyline.set("fill", "none")

    # write xml back to svg
    svg.write(out_file)


def convert_svg_to_24bit_png(in_file, out_file, export_size):
    """Convert SVG to PNG using Inkscape"""
    # convert svg file to png
    print("Converting SVG to PNG...")

    temp_file = out_file.replace(".png", "_temp.png")
    subprocess.call(
        f'inkscape -o {out_file} --export-id="terrain" --export-height={export_size} --export-width={export_size} {in_file}',
        # f"libreoffice --headless --convert-to png --outdir {out_dir} {in_file}",
        shell=True,
    )
    print("Converted SVG to PNG")
    # print("Converting PNG to 24-bit...")
    # subprocess.call(
    #     f"convert {temp_file} -alpha off {out_file}",
    #     shell=True,
    # )
    # print("Converted PNG to 24-bit, saved as", out_file)
    # print("Deleting temp file...")
    # os.remove(temp_file)
    # print("Deleted temp file")


def generate_heightmap(in_file, out_file):
    """Convert DEM (XYZ or ASC) to GeoTIFF"""

    subprocess.call(
        f"gdaldem hillshade -alg Horn -alt 45 -multidirectional -of PNG {in_file} {out_file}",
        shell=True,
    )


def generate_colorrelief(in_file, out_file):
    """Convert DEM (XYZ or ASC) to GeoTIFF"""

    subprocess.call(
        f"gdaldem color-relief -of PNG {in_file} ./modules/colorrelief.txt {out_file}",
        shell=True,
    )
