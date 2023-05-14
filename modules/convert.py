# convert XYZ to lat/lon
from pyproj import Proj, transform, Transformer
import rasterio
import numpy as np

import subprocess
import os
import re

def get_color(colors, color):
    if color in colors:
        return colors[color]
    else:
        return color


XY_LATLON_PROJ = Transformer.from_crs(3857, 4326, always_xy=True, accuracy=0.01, allow_ballpark=False)
LATLON_XY_PROJ = Transformer.from_crs(4326, 3857, always_xy=True)

def convert_xy_latlon(x, y):
    # return XY_LATLON_PROJ.transform(float(x) + START_XY[0], -float(y) + START_XY[1])
    return XY_LATLON_PROJ.transform(float(x), -float(y))
    # return (float(x), float(y))

def convert_latlon_xy(x, y):
    return LATLON_XY_PROJ.transform(float(x), float(y))

START_XY = convert_latlon_xy(25.0066402797,39.7920342634)

def convert_to_geojson(worldname, path):
    shpString = (path.split('/')[-1])  
    subprocess.call(f'ogr2ogr -f "GeoJSON" -t_srs "EPSG:4326" -s_srs "EPSG:3857" output/{worldname}/{shpString}.geojson temp/{worldname}/{shpString}/{shpString}.shp', shell=True)
    print('Wrote', shpString, 'to GeoJSON')

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    hlen = len(hex)
    return tuple(int(hex[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))


def translate_xyz_to_geotiff(worldname, terrain_bounds):
    in_file = f'input/{worldname}/dem.xyz'
    gridded_heightmap_str = f'output/{worldname}/gridded_heightmap.tif'
    standard_heightmap_str = f'output/{worldname}/heightmap.tif'

    # if input/{worldname}.xyz doesn't exist, return
    if not os.path.exists(in_file):
        print(f'No XYZ file found ({in_file}), skipping...')
        return False
    else:
      print(f'Found XYZ file ({in_file}), processing heightmap...')


    # if standard_heightmap_str exists, remove it
    if os.path.exists(standard_heightmap_str):
        os.remove(standard_heightmap_str)

    print('Applying projection and converting to GeoTIFF...')
    subprocess.call(f'gdalwarp -s_srs "EPSG:3857" -t_srs "EPSG:4326" -srcnodata 0 -of "GTiff" {in_file} {standard_heightmap_str}', shell=True)
    print(f'Projection applied, saved as {standard_heightmap_str}')

    # FILL nodata values
    print('Filling nodata values...')
    subprocess.call(f'gdal_fillnodata.py -md 100 {standard_heightmap_str} {standard_heightmap_str}', shell=True)

    print('Shifting heightmap to match terrain bounds...')
    subprocess.call(f'gdal_edit.py -a_ullr {terrain_bounds[0][0]} {(terrain_bounds[0][1])} {terrain_bounds[2][0]} {terrain_bounds[2][1]} {standard_heightmap_str}', shell=True)

    return standard_heightmap_str

def generate_hillshade(heightmap, output):
    # generate hillshade from heightmap
    subprocess.call(f"gdaldem hillshade -of GTiff -b 1 -z 1.0 -s 1.0 -az 135.0 -compute_edges -s 1 -alg ZevenbergenThorne -igor {heightmap} {output}", shell=True)

def generate_slope(heightmap, output):
    # generate slope from heightmap
    subprocess.call(f"gdaldem slope -of GTiff -s 1 -compute_edges {heightmap} {output}", shell=True)
