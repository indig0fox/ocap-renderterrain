from pyproj import Transformer


XY_LATLON_PROJ = Transformer.from_crs(
    3857, 4326, always_xy=True, accuracy=0.01, allow_ballpark=False
)
LATLON_XY_PROJ = Transformer.from_crs(4326, 3857, always_xy=True)


def convert_xy_latlon(x, y):
    """Converts XY coordinates to lat/lon coordinates"""
    # return XY_LATLON_PROJ.transform(float(x) + START_XY[0], -float(y) + START_XY[1])
    return XY_LATLON_PROJ.transform(float(x), -float(y))
    # return (float(x), float(y))


def convert_latlon_xy(x, y):
    """Converts lat/lon coordinates to XY coordinates"""
    return LATLON_XY_PROJ.transform(float(x), float(y))
