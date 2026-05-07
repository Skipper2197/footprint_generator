# 🛰️ footprint_generator

A lightweight Python GUI application designed to extract geospatial footprints from satellite imagery (TIFF) and export them into various vector formats.

![Application Preview](app_demo.png)

## 🌟 Features

* **TIFF Analysis**: Automatically calculates the geospatial boundary (footprint) of `.tif` and `.tiff` files.
* **Visual Preview**: Integrated plotting to view the satellite data and its calculated footprint before exporting.
* **Batch Processing**: "Process All" functionality to handle entire directories of imagery at once.
* **Multi-Format Export**: Support for common geospatial formats including **GeoJSON** and more.
* **Modern Python Stack**: Built with **PySide6** for the interface and managed with **uv** for lightning-fast dependency handling.

## 🚀 Getting Started

### Prerequisites

You will need `uv` installed on your system. If you don't have it yet, install [uv](https://github.com/astral-sh/uv):

~~~bash
git clone https://github.com/Skipper2197/footprint_generator.git
cd footprint_generator
uv sync
uv run main.py
~~~