# OCAP Terrain Renderer

This is a Docker image for the OCAP Terrain Renderer.

## Usage

### Input Data

The input data is expected to be in the `input` directory. The input data should be in the following format:

    input
    ├── {worldName}
    │   ├── dem.xyz
    │   ├── meta.json
    │   ├── {worldName}.emf

To acquire them:

| Input Data | Source |
| ---------- | ------ |
| dem.xyz |  [get_heightmap.sqf](./resources/data_tools/README.md#get_heightmapsqf) |
| meta.json | [get_metadata.sqf](./resources/data_tools/README.md#get_metadatasqf) |
| {worldName}.emf | [EXPORTNOGRID Cheat (see TOPOGRAPHY)](https://community.bistudio.com/wiki/Arma_3:_Cheats)

### Output Data

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
docker build -t indifox926/ocap-renderterrain .

docker run -it --rm --name ocap-renderterrain --mount type=bind,src="$(pwd)"/input,target=/app/input --mount type=bind,src="$(pwd)"/output,target=/app/output --mount type=bind,src="$(pwd)"/temp,target=/app/temp --mount type=bind,src="$(pwd)"/geojson,target=/app/geojson indifox926/ocap-renderterrain:latest
```