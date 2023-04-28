[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![ci](https://github.com/Deltares/netcdf_to_gltf_converter/actions/workflows/build.yml/badge.svg)](https://github.com/Deltares/netcdf_to_gltf_converter/actions/workflows/build.yml)
[![quality gate](https://sonarcloud.io/api/project_badges/measure?project=Deltares_netcdf_to_gltf_converter&metric=alert_status)](https://sonarcloud.io/dashboard?id=Deltares_netcdf_to_gltf_converter)

# D-HYDRO NetCDF output to glTF converter

This is a tool that converts D-HYDRO map output results that are stored in the NetCDF file format to the glTF file format. The goal is to allow users who work with D-HYDRO results to view their data in 3D renderers using the glTF format.

<p align="center">
  <img src="docs/readme/img/result.gif" alt="animated" />
</p>


## Why use glTF?
glTF (GL Transmission Format) is an open-standard file format developed by The Khronos Group. The glTF file format is used for 3D scenes and models designed for efficient transmission and loading of 3D content on the web and other real-time applications. This file format can store geometry, materials, textures, animations, and other scene data.
glTF is used in a variety of industries and applications, including gaming, virtual and augmented reality, education, and more. It is particularly well-suited for web-based applications, as it allows 3D content to be easily and efficiently delivered over the internet, and can be rendered in real-time on a wide range of devices. 

# User guide
## Requirements
- Python >=3.9, <3.12
- Poetry >=1.4.2 

## Installation
1. Install dependency manager [Poetry](https://python-poetry.org/docs/):

**Windows (PowerShell)**
```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**Linux, macOS, Windows (WSL)**
```
curl -sSL https://install.python-poetry.org | python3 -
```
2. Clone or [download](https://github.com/Deltares/netcdf_to_gltf_converter/archive/refs/heads/main.zip) this repository to your local machine
3. From the root folder, open your command line and execute:
```
poetry install
```

These steps will ensure that the converter is installed within a virtual environment (`.venv`) and you can start calling the converter script.

## Usage
 After following the installation steps, the converter can be used from the command line. 
 Two arguments should be passed to the converter script.
 * The first argument is the path to the source NetCDF file. Only files with the following conventions are supported: `CF-1.8 UGRID-1.0 Deltares-0.10`
 * The second argument is the path to the target glTF file. If the path already exist it will be overwritten.
 
**Example**
 ```
 poetry run python input_map.nc output.gltf
 ```
 
## View results
 Several glTF viewers exist that can be used to view the produced glTF file. Just drag and drop the file and the glTF file is rendered.
 * [glTF Sample Viewer](https://github.khronos.org/glTF-Sample-Viewer-Release/)
 * [Babylon.js Sandbox](https://sandbox.babylonjs.com/)

# Contributing
If you encounter any issues or have good ideas for this project please [create an issue](https://github.com/Deltares/netcdf_to_gltf_converter/issues/new/choose). This will help improve the project.bBefore creating any new issues, please check the [backlog](https://github.com/Deltares/netcdf_to_gltf_converter/issues) to see if your issue already exists. 

# Acknowledgments
[Connec2](https://connec2.nl/) is a company specialized in cross reality (XR) technology that guided us to setup this project. 
This tool was developed as part of the fifth Top consortium for Knowledge and Innovation (TKI) programme.

