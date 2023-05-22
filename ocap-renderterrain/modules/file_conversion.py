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


    forests_polygons = get_svg_items(svg_root, "forests", "polygon")
    # if count of forest polygons is > 150000, compress the SVG
    if len(forests_polygons) > 250000:
        # get forests root
        forests = svg_root.find("./{http://www.w3.org/2000/svg}g[@id='forests']")
        # remove forests from svg
        for forest in forests:
            forests.remove(forest)



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

    print("Processing forests...")
    forests_polygons = get_svg_items(svg_root, "forests", "polygon")
    # for all polygons under <g id="forests">, add fill-opacity=0.5
    for polygon in forests_polygons:
        polygon.set("fill-opacity", "0.2")
        polygon.set("fill", "#3e6e30")


         
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


def generate_svg_dark(in_file, out_file):
    """Change some of the default colors to make a 'dark' version of the SVG"""
    # read SVG as XML for parsing
    print("Reading SVG...")
    svg = ET.parse(in_file)
    svg_root = svg.getroot()
    if svg_root is None:
        print(f"Failed to parse SVG file ({in_file}), exiting...")
        sys.exit(1)

    print("Processing countLines")
    count_lines = get_svg_items(svg_root, "countLines", "polyline")
    if count_lines is not None:
      # reduce opacity of countLines
      for polyline in count_lines:
          polyline.set("opacity", "0.5")
    
    print("Processing land...")
    land = get_svg_items(svg_root, "terrain", "polygon")
    if land is not None:
      # darken land
      for land_el in land:
        land_el.set("fill", "#1d2b20")

    print("Processing sea...")
    sea = get_svg_items(svg_root, "terrain", "rect")
    if sea is not None:
      # darken sea
      for sea_el in sea:
        sea_el.set("fill", "#303d6e")

    print("Brightening text...")
    town_names = get_svg_items(svg_root, "townNames", "text")
    if town_names is not None:
      # brighten location names
      for text in town_names:
        text.set("fill", "#EEEEEE")
        text.set("stroke", "#0f0f0f")
        text.set("stroke-width", "1px")
        text.set("font-weight", "bold")
    mountains = get_svg_items(svg_root, "mountains", "text")
    if mountains is not None:
      # brighten mountain height markers
      for text in mountains:
        text.set("fill", "#EEEEEE")
        # text.set("stroke", "#0f0f0f")
        # text.set("stroke-width", "1px")
        # text.set("font-weight", "bold")

    # write xml back to svg
    svg.write(out_file)

def generate_svg_landonly(in_file, out_file):
    """Create an SVG that only has land and sea layers for us to overlay analysis layers."""
    # read SVG as XML for parsing
    print("Reading SVG...")
    svg = ET.parse(in_file)
    svg_root = svg.getroot()
    if svg_root is None:
        print(f"Failed to parse SVG file ({in_file}), exiting...")
        sys.exit(1)
    
    # get all <g> elements
    gs = svg_root.findall("./{http://www.w3.org/2000/svg}g")
    # remove all <g> elements except for terrain
    for g in gs:
      if g.get("id") != "terrain":
        svg_root.remove(g)

    # write xml back to svg
    svg.write(out_file)

def generate_svg_noland(in_file, out_file):
    """Create an SVG that has everything above the terrain layers, to render over analysis layers (except forests which need opacity)."""
    # read SVG as XML for parsing
    print("Reading SVG...")
    svg = ET.parse(in_file)
    svg_root = svg.getroot()
    if svg_root is None:
        print(f"Failed to parse SVG file ({in_file}), exiting...")
        sys.exit(1)
    
    # get all <g> elements where id=terrain
    gs = svg_root.findall("./{http://www.w3.org/2000/svg}g")
    # remove all <g> elements except for terrain
    for g in gs:
      if g.get("id") == "terrain":
        svg_root.remove(g)

    # write xml back to svg
    svg.write(out_file)

# def generate_svg_forestonly(in_file, out_file):
#     """Create an SVG that has everything above the terrain layers, to render over analysis layers."""
#     # read SVG as XML for parsing
#     print("Reading SVG...")
#     svg = ET.parse(in_file)
#     svg_root = svg.getroot()
#     if svg_root is None:
#         print(f"Failed to parse SVG file ({in_file}), exiting...")
#         sys.exit(1)
    
#     # get all <g> elements where id=terrain
#     gs = svg_root.findall("./{http://www.w3.org/2000/svg}g")
#     # remove all <g> elements except for terrain
#     for g in gs:
#       if g.get("id") != "forests":
#         svg_root.remove(g)

#     # write xml back to svg
#     svg.write(out_file)

def convert_svg_to_png(in_file, out_file, export_size):
    """Convert SVG to PNG using Inkscape"""
    # convert svg file to png
    print("Converting SVG to PNG...")

    temp_file = out_file.replace(".png", "_temp.png")
    subprocess.call(
        f'inkscape -o {out_file} --export-height={export_size} --export-width={export_size} {in_file}',
        # f"libreoffice --headless --convert-to png --outdir {out_dir} {in_file}",
        shell=True,
    )
    print("Converted SVG to PNG")


def convert_png_to_24bit(in_file, out_file):
    """Convert PNG to 24-bit"""
    print("Converting PNG to 24-bit...")

    ret_code = subprocess.call(
        f"convert {in_file} -alpha off {out_file}",
        shell=True,
      )
    if ret_code != 0:
        print("Error converting PNG to 24-bit, exiting...")
        sys.exit(1)
    print("Converted PNG to 24-bit, saved as", out_file)


def generate_heightmap(in_file, out_file, export_size):
    """Convert DEM (XYZ or ASC) to GeoTIFF"""

    subprocess.call(
        f"gdaldem hillshade -alg Horn -alt 45 -multidirectional -of PNG {in_file} {out_file}",
        shell=True,
    )
    # resize to export_size
    subprocess.call(
        f"convert {out_file} -resize {export_size}x{export_size} {out_file}",
        shell=True,
    )

def generate_colorrelief(in_file, out_file, export_size):
    """Convert DEM (XYZ or ASC) to GeoTIFF"""

    # see here for other color relief options
    # http://soliton.vm.bytemark.co.uk/pub/cpt-city/index.html
    subprocess.call(
        f"gdaldem color-relief -of PNG {in_file} ./modules/nzblue.cpt {out_file}",
        shell=True,
    )
    # resize to export_size
    subprocess.call(
        f"convert {out_file} -resize {export_size}x{export_size} {out_file}",
        shell=True,
    )

def set_half_opacity(in_file, out_file):
    """Set image to half opacity"""
    subprocess.call(
        f"convert {in_file} -alpha set -channel a -evaluate set 50% {out_file}",
        shell=True,
    )

def composite_images(in_file, overlay_file, out_file):
    """Composite two PNGs"""
    # overlay filter
    subprocess.call(
        f"convert {in_file} {overlay_file} -composite {out_file}",
        shell=True,
    )

def overlay_images(in_file, overlay_file, out_file):
    """Overlay two PNGs"""
    # overlay filter
    subprocess.call(
        f"convert {in_file} {overlay_file} -compose overlay -composite {out_file}",
        shell=True,
    )

def multiply_images(in_file, overlay_file, out_file):
    """Multiply two PNGs"""
    # multiply filter
    subprocess.call(
        f"convert {in_file} {overlay_file} -compose multiply -composite {out_file}",
        shell=True,
    )