# Gaussian Viewer

A lightweight WebGL-based viewer for 3D Gaussian Splatting models. This viewer allows you to interactively visualize and navigate through 3D Gaussian Splat models in your web browser.

## Features

- Real-time rendering of 3D Gaussian Splats
- Interactive camera controls (orbit, pan, zoom)
- Support for PLY file format
- Fast C-optimized data processing
- WebGL-based rendering
- Dynamic model switching
- Multiple navigation modes (keyboard, mouse, touch, gamepad)

## Installation

```bash
pip install -e .
```
or 
```bash
pip install gaussian-viewer
```

## Usage

Basic usage example:

```python
from gaussian_viewer import GaussianViewer
from gaussian_viewer._splat_writer import write_splat_data
from plyfile import PlyData
import numpy as np
from io import BytesIO

def process_ply_to_splat(ply_path):
    """Convert PLY file to SPLAT format"""
    plydata = PlyData.read(ply_path)
    # Process PLY data...
    return splat_data

# Create viewer and show PLY
viewer = GaussianViewer(port=6789)
splat_data = process_ply_to_splat("path/to/your.ply")
viewer.show(splat_data)

# Open in browser (optional)
viewer.open_in_browser()
```
## Controls

- **Mouse/Trackpad**:
  - Click and drag: Orbit view
  - Right click drag: Move forward/back
  - Scroll: Orbit view
  - Ctrl + scroll: Move forward/back
  - Shift + scroll: Move up/down
  - Pinch: Zoom

- **Keyboard**:
  - Arrow keys: Move forward/back/left/right
  - WASD: Tilt/turn camera
  - QE: Roll camera
  - IJKL: Alternative orbit controls
  - Space: Jump up
  - 0-9: Switch camera views
  - P: Reset animation

- **Touch (Mobile)**:
  - One finger: Orbit
  - Two fingers: Pan and zoom
  - Two finger rotate: Roll camera

## Requirements

- Python >= 3.8
- NumPy
- aiohttp
- plyfile
- A modern web browser with WebGL support

## License

MIT License

