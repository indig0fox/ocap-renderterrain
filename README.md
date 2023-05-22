# Terrain Rendering for OCAP2

## Overview/History

This extraction tool and Docker processing pipeline is intended for use with [OCAP2](https://github.com/OCAP2/OCAP). It's meant to make it easier to capture and render raster tilesets for use with the web playback viewer.

The first "Render2.0" tilesets were created back in April of 2022 and consist of four distinct tilesets:

- "topo" - A map closely resembling the one in-game. This is the default tileset.
- "topoDark" - A dark version of the topo tileset, to scare the light-mode users.
- "topoRelief" - A topo tileset with a hillshaded base to accentuate terrain contours.
- "colorRelief" - A color relief tileset with flat colors representing elevation and no hillshading.

Support for utilizing these tilesets was added into the beta web viewer around the same time, but the tilesets themselves were more difficult to render as EMF exports were still utilized. This also lowered the end quality as per-layer tweaking wasn't possible to refine the end product.

In addition, the difficulty of the process and the footprint of its system-level requirements were undesirable. This pipeline seeks to solve for that by utilizing Docker to provide a consistent and portable environment for processing the data.

This pipeline seeks to solve for that, and while initial setup to capture the raw data involves setting up and using the diagnostics exe, the end result is a much higher quality tileset rendered at 1px/m resolution with layer adjustments to provide a concise and accurate representation of the terrain in a static tile format.

> **Core changes:**
>
> - Forests are now darker and partially transparent.
> - Color relief now uses a custom color palette from -450m to 600m.
> - Dark mode has been improved.
> - Hillshading no longer covers features.
> - Heightmap extraction now uses the more efficient ASCII grid format.
>
> **Things that haven't changed:**
>
> - Due to the large number of terrains already rendered, altering the CRS OCAP2 uses for rendering distances accurately in real-world space would be a breaking change. As such, the CRS is still set CRS.Simple and map-based distance measurements are wildly inaccurate. For these reasons, the tilesets are not georeferenced and are only intended for use with the web viewer. _For georeferenced vector tiles, see [arma3-geoAAR](https://github.com/indig0fox/arma3-geoAAR). There is a branch with support for these, but this feature has not been fully implemented due to hosting and adoption concerns._
> - The resulting folder structure is backwards-compatible and can be used even on the stable branch of OCAP2/web. If space is a concern, and your version does not support the new tilesets, you can delete the `topoRelief`, `topoDark`, and `colorRelief` folders. Please make sure that you also update the corresponding boolean values in `map.json` to `false` to prevent error should you update in the future.

---

## Project File Structure

    | ocap-renderterrain
    ├── ocap-exporter (Arma3 extension and SQF script)
    ├───── ocap_exporter.go (extension source)
    ├───── ocap_exporter_x64.dll (extension binary)
    ├───── export_data.sqf (SQF script)
    ├── ocap-renderterrain (Docker pipeline)

---

## Gathering Input Data

The following steps are designed to be run in sequence.

> **One Time Step**:
> _Copy `./ocap-exporter/ocap_exporter_x64.dll` to the root of your Arma 3 installation. This extension must be callable by Arma to facilitate data export to file._

### Export SVG

Running the `diag_exportTerrainSVG` command to provide the best quality export requires running the Diagnostic executable of Arma 3. This requires a little setup to prepare, but is worth it for the quality of the export.

1. In your Steam library, right click on Arma 3 and select `Properties`.
1. Click the `BETAS` tab.
1. In the dropdown, select `Development - Development Build`.
1. Close the properties window and run the pending update.
1. Navigate to your Arma 3 installation directory.

In order to still utilize the easy-mode of the launcher to manage what mods we want to load (i.e. the addons that give the maps to render), we'll tease the launcher into running the diagnostic executable.

1. Rename `arma3_64.exe` to `arma3_64.exe.bak`.
1. Rename `arma3diag_x64.exe` to `arma3_64.exe`.

> Launch `Arma3Root\arma3launcher.exe` **AS ADMINISTRATOR** to open the launcher.

Now, when we launch Arma 3 by clicking Play, we'll be running the diagnostic executable. This will allow us to run the `diag_exportTerrainSVG` command. This process is included in the `./ocap-exporter/export_data.sqf` script, and will save the SVG to the root of your Arma 3 installation.

> You can verify you're running the diagnostics exe if, when Arma 3 is launched, the icon in your taskbar is GREEN.

> Note: If you're getting a syntax error near `diag_exportTerrainSVG`, you're NOT running the diagnostic executable. Check the steps above.

### Export Heightmap

1. Open the desired terrain in the 3DEN Editor.
1. Open the debug console using `Ctrl-D` (if CBA is loaded), or via the Tools menu at the top of the editor.
1. Copy the contents of `./ocap-exporter/export_data.sqf` to your clipboard (`Ctrl-C`) then paste it into the debug console (`Ctrl-V`) and press `Local Exec`.
1. **The SVG will capture and nothing will appear to happen. On the largest maps, it may take up to 10 seconds to complete.**
1. **When the SVG has finished exporting, a loading screen will appear while the heightmap is exported. This may take up to 60 seconds on large maps.**
1. Once the loading screen closes, close the debug console. Some details will be printed in systemChat. You don't need to make note of these.

In the root of your Arma 3 installation, locate the folder titled `ocap_exporter`. In this, a folder will have been created with the `worldName` of the map you exported. Copy or Cut this folder to the `./input` directory.

> Exporter logs can also be found in the `Arma3Root/ocap_exporter/<worldName>` folder. These can be useful for debugging or opening an issue if something goes wrong.

> Note: If you're getting a syntax error near `diag_exportTerrainSVG`, you're NOT running the diagnostic executable. Check the steps in the previous section.

---

### Input Data Structure

The input data is expected to be in the `input` directory of this project. The input data should be in the following format:

    input
    ├── {worldName}
    │   ├── {worldName}.asc (heightmap)
    │   ├── {worldName}.svg (map features)
    │   ├── map.json (metadata)
    |   └── ocap_exporter.log (log of export)

### Other Details

| Input Data                 | Source                                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------------------ |
| {worldName}.asc                    | export_data.sqf                                                                                        |
| map.json                   | export_data.sqf                                                                                        |
| {worldName}.svg            | [diag_exportTerrainSVG](https://community.bistudio.com/wiki/diag_exportTerrainSVG) via export_data.sqf |
| ocap_exporter.log          | a log of capture |

---

## Processing (Docker)

### Requirements

- You should have Docker Engine installed and running. See [Docker Engine](https://docs.docker.com/engine/install/) for installation instructions.

### Processing Pipeline

> Note: You may see inkscape errors during image processing. These are expected (related to not having a gui server to connect to) and can be ignored.

```cmd
git clone https://github.com/indig0fox/ocap-renderterrain
cd ./ocap-renderterrain
```

```docker
# now from the project root

cd ./ocap-renderterrain

docker build -t indifox926/ocap-rendermap:latest .


<!-- WITHOUT TEMP MOUNTED, FOR SPEED -->
docker run -it --rm --name ocap-rendermap --mount type=bind,src="$(pwd)"/input,target=/app/input --mount type=bind,src="$(pwd)"/output,target=/app/output indifox926/ocap-rendermap:latest

<!-- WITH TEMP BIND MOUNTED FOR DEBUG -->
docker run -it --rm --name ocap-rendermap --mount type=bind,src="$(pwd)"/input,target=/app/input --mount type=bind,src="$(pwd)"/output,target=/app/output --mount type=bind,src="$(pwd)"/temp,target=/app/temp indifox926/ocap-rendermap:latest
```

### Output Data Structure

The output data will be saved to the `output` directory of this project. The output data will be in the following format:

    output
    ├── {worldName}
    │   ├── topo
    │   │   ├── {z}
    │   │   │   ├── {x}
    │   │   │   │   ├── {y}.png
    │   │   │   │   ├── {y}.png.aux.xml
    │   │   │   ├── ...
    │   │   │   └── {x}
    │   │   ├── ...
    │   │   └── {z}
    │   ├── topoDark
    |   |   └─ <same format as above>
    │   ├── topoRelief
    │   |   └─ <same format as above>
    │   └── colorRelief
    │   |    └─ <same format as above>
    |   ├── {worldName}_colorRelief.tif (georeferenced GeoTiff)
    |   ├── {worldName}_topoRelief.tif (georeferenced GeoTiff)
    |   └── map.json (metadata)

This folder can be installed directly to the local /maps folder of an OCAP2 instance. Please also provide this data to [indigo@indigofox.dev](mailto:indigo@indigofox.dev) or on the OCAP2 Discord server so that it can be hosted for others to stream.

## Credits

- Foundation of heightmap export script to XYZ geo-format by [Beowulf Strategic Operations](https://beowulfso.com/)
- Color relief shading profiles adapted from [NZBlue](http://soliton.vm.bytemark.co.uk/pub/cpt-city/em/index.html) and the [USGS](http://soliton.vm.bytemark.co.uk/pub/cpt-city/usgs/tn/usgs.png.index.html)
- [code34](https://github.com/code34) for enabling me to write extensions in Go
- Bohemia Interactive for adding SVG export capabilities to their engine
