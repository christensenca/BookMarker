#!/bin/bash
# Build script for BookMarker app
echo "Building BookMarker executable..."
pyinstaller --onefile --add-data "app:app" run.py
echo "Build complete! Executable is in dist/run"