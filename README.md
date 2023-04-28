[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![ci](https://github.com/Deltares/netcdf_to_gltf_converter/actions/workflows/build.yml/badge.svg)](https://github.com/Deltares/netcdf_to_gltf_converter/actions/workflows/build.yml)
[![quality gate](https://sonarcloud.io/api/project_badges/measure?project=Deltares_netcdf_to_gltf_converter&metric=alert_status)](https://sonarcloud.io/dashboard?id=Deltares_netcdf_to_gltf_converter)

# D-HYDRO NetCDF output to glTF converter

This is a tool that converts D-HYDRO map output results that are stored in the NetCDF file format to the glTF file format. The goal is to allow users who work with D-HYDRO results to view their data in 3D renderers using the glTF format.

## Why use glTF?
glTF (GL Transmission Format) is an open-standard file format developed by The Khronos Group. The glTF file format is used for 3D scenes and models designed for efficient transmission and loading of 3D content on the web and other real-time applications. This file format can store geometry, materials, textures, animations, and other scene data.
glTF is used in a variety of industries and applications, including gaming, virtual and augmented reality, education, and more. It is particularly well-suited for web-based applications, as it allows 3D content to be easily and efficiently delivered over the internet, and can be rendered in real-time on a wide range of devices. 

## Requirements
- Python >=3.9, <3.12
- [Poetry](https://python-poetry.org/docs/) >=1.4.2 

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
2. Clone this repository to your local machine
<img src="docs/installation/img/download.png"  width=30% height=30%>

3. From the root folder, open your command line and execute:
```
poetry install
```
## Example
