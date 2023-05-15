# OCAP Terrain Renderer

This is a Docker image for the OCAP Terrain Renderer.

## Gathering Input Data

The following steps are designed to be run in sequence.

> **One Time Step**:
> _Copy `./resources/data_tools/a3exporter/ocap_exporter_x64.dll` to the root of your Arma 3 installation. This extension must be callable by Arma to facilitate data export to file._

### Export EMF !(Deprecated)

1. Launch Arma 3 **as Administrator** with the addon that holds the map you want to render. This is usually best done by running `arma3launcher.exe` from the root of your Arma 3 installation as administrator, loading your addons, then clicking the `Play` button. This will ensure write permissions do not prevent the export.
1. Click "Editor" from the main menu, then click once to select the map. Press `Ctrl-O` to open the **2D Editor**.
1. Hold `Left Shift` and press `Numpad -`. Release `Left Shift`. Type `EXPORTNOGRID`.
1. The game may freeze briefly depending on map size. You will see a flicker near the top left of the screen indicating the export is complete.

Navigate to `C:\`. Locate the file `{worldName}.emf` and keep it available for the next step.

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

Now, when we launch Arma 3 by clicking Play, we'll be running the diagnostic executable. This will allow us to run the `diag_exportTerrainSVG` command. This process is included in the `./resources/data_tools/export_data.sqf` script, and will save the SVG to the root of your Arma 3 installation.

> You can verify you're running the diagnostics exe if, when Arma 3 is launched, the icon in your taskbar is GREEN.

> Note: If you're getting a syntax error near `diag_exportTerrainSVG`, you're NOT running the diagnostic executable. Check the steps above.

### Export Heightmap

1. Place a unit by double clicking on the map and pressing OK.
1. At the top of the screen, click "Preview".
1. Once loaded into the mission, press `Esc` to open the pause menu.
1. Copy the contents of `./resources/data_tools/export_data.sqf` to your clipboard (`Ctrl-C`) then paste it into the debug console (`Ctrl-V`) and press `Local Exec`.
1. A loading screen will appear and the progress bar at the top will diminish as the terrain information is gathered.
1. Once the loading screen closes, press `Esc` to close the pause menu.
1. A hint will be shown in the top right to indicate the export is saving. Once it states `Saved!`, the export is complete.

In the root of your Arma 3 installation, locate the folder titled `ocap_exporter`. In this, a folder will have been created with the worldName of the map you exported. Copy or Cut this folder to the `./input` directory.

> Note: If you're getting a syntax error near `diag_exportTerrainSVG`, you're NOT running the diagnostic executable. Check the steps in the previous section.

### Render EMF to PNG

`./resources/data_tools/EmfToPng.exe`

### Data Structure

The input data is expected to be in the `input` directory of this project. The input data should be in the following format:

    input
    ├── {worldName}
    │   ├── {worldName}.emf
    │   ├── {worldName}.xyz
    │   ├── map.json
    |   └── ocap_exporter.log

### Other Details

| Input Data      | Source                                                                                    |
| --------------- | ----------------------------------------------------------------------------------------- |
| dem.xyz         | export_data.sqf                                                                           |
| map.json        | export_data.sqf                                                                           |
| {worldName}.emf | [EXPORTNOGRID Cheat (see TOPOGRAPHY)](https://community.bistudio.com/wiki/Arma_3:_Cheats) |

## Output Data

The output data will be in the `output` directory. The output data will be in the following format:

    output
    ├── {worldName}
    │   ├── 0
    │   ├── 1
    │   ├── 2
    │   ├── 3
    │   ├── 4
    │   ├── 5
    │   ├── 6
    │   ├── map.json
    │   ├── leaflet.html

### Running

    ```docker
    cd ./ocap-exporter

    docker build -t indifox926/ocap-rendermap:latest .

    docker run -it --rm --name ocap-rendermap --mount type=bind,src="$(pwd)"/input,target=/app/input --mount type=bind,src="$(pwd)"/output,target=/app/output --mount type=bind,src="$(pwd)"/temp,target=/app/temp indifox926/ocap-rendermap:latest
    ```

## Credits

- Foundation of heightmap export script to XYZ geo-format by [Beowulf Strategic Operations](https://beowulfso.com/)
