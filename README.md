# GeoJSON Footprint Generator

<u>Developed by Helena Beinhacker, David Bunich, and Ian Cullicott.</u>

The GeoJSON Footprint Generator is a specialized GIS utility designed to automate the extraction of precise geographic boundaries from raster data and provide a user-friendly experience for those who prefer not to . By filtering out "no-data" artifacts and calculating the geometry of valid pixels, it transforms raw TIFF imagery into clean, usable GeoJSON footprints. Other file formats are also available for exporting.

![Application Preview](app_demo.png)

## Features

* **TIFF Analysis**: Automatically calculates the geospatial boundary (footprint) of `.tif` and `.tiff` files.
* **User-Friendly UI**: Built with PySide6, providing a modern, cross-platform desktop experience for GIS analysts.
* **Visual Preview**: Integrated plotting to view the satellite data and its calculated footprint before exporting.
* **Batch Processing**: "Process All" functionality to handle entire directories of imagery at once. All exports are put into the provided "exports" folder.
* **Multi-Format Export**: Support for common geospatial formats including **GeoJSON** and more.
* **Multi-CRS Export**: Support for common coordinate reference systems. See below for the basic available options.

## Getting Started

### Prerequisites

You will need `uv` installed on your system. If you don't have it yet, install [uv](https://github.com/astral-sh/uv):

1. Clone the repository *(Ran once if performed correctly)*
~~~bash
git clone https://github.com/Skipper2197/footprint_generator.git
cd footprint_generator
~~~
2. Sync dependencies and run *(Ran for every use)*
~~~bash
uv sync
uv run main.py
~~~


## Why this project?
The goal is to provide a user-friendly interface that simplifies complex GIS workflows, making it easier for users to visualize and process geographic data without manual intervention

## CRS Options
You can select to export your file into different coordinate reference systems, such as:
  * **WGS84**: globaly centered standard coordinate system for cartography, geospatial data, and GPS
  * **Web Mercator**: commonly used for web mapping
  * **NAD83**: standard coordinate system for North American maps
  etc.

This list is easily modifiable according to your preferences, given that you know the EPSG codes for your desired coordinate reference systems.