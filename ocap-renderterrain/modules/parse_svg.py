import sys
import os
import xml.etree.ElementTree as ET

def parse_svg_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    categories = root.findall('./{http://www.w3.org/2000/svg}g')

    # Get standard color definitions
    colors = {}
    for container in root.findall('./{http://www.w3.org/2000/svg}defs'):
        for item in container.findall('./{http://www.w3.org/2000/svg}linearGradient'):
            colors.update({
              item.get('id'): item.find('./{http://www.w3.org/2000/svg}stop').get('stop-color')
            })
    # print(colors)
    return (root, categories, colors)

