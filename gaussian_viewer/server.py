import os
from aiohttp import web
import pkg_resources
import numpy as np
from io import BytesIO
from plyfile import PlyData
import hashlib
import time

class GaussianServer:
    def __init__(self, port: int):
        self.port = port
        self.app = web.Application()
        self.splat_data = None
        self.data_hash = None
        self.last_modified = 0
        
        # Setup routes
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/ply', self.handle_ply)
        self.app.router.add_head('/ply/check', self.handle_ply_check)
        
        # Add static route for web files
        web_path = pkg_resources.resource_filename('gaussian_viewer', 'web')
        self.app.router.add_static('/', web_path)
        
        # Add CORS headers
        self.app.router.add_options('/{tail:.*}', self.handle_options)

    def _cors_response(self, response):
        """Add CORS headers to response"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    async def handle_options(self, request):
        return self._cors_response(web.Response())

    async def handle_index(self, request):
        index_path = pkg_resources.resource_filename('gaussian_viewer', 'web/index.html')
        return self._cors_response(web.FileResponse(index_path))

    async def handle_ply_check(self, request):
        """Handle HEAD request to check if data has changed"""
        if self.splat_data is not None:
            response = web.Response()
            response.headers['ETag'] = f'"{self.data_hash}"'
            response.headers['Last-Modified'] = str(self.last_modified)
            return self._cors_response(response)
        return web.Response(status=404)

    async def handle_ply(self, request):
        if self.splat_data is not None:
            response = web.Response(body=self.splat_data)
            response.headers['ETag'] = f'"{self.data_hash}"'
            response.headers['Last-Modified'] = str(self.last_modified)
            return self._cors_response(response)
        return web.Response(status=404, text="PLY data not found")

    def process_ply_data(self, plydata):
        """Convert PLY data to SPLAT format directly in memory"""
        vert = plydata["vertex"]
        sorted_indices = np.argsort(
            -np.exp(vert["scale_0"] + vert["scale_1"] + vert["scale_2"])
            / (1 + np.exp(-vert["opacity"]))
        )
        
        buffer = BytesIO()
        for idx in sorted_indices:
            v = plydata["vertex"][idx]
            position = np.array([v["x"], v["y"], v["z"]], dtype=np.float32)
            scales = np.exp(
                np.array([v["scale_0"], v["scale_1"], v["scale_2"]], dtype=np.float32)
            )
            rot = np.array([v["rot_0"], v["rot_1"], v["rot_2"], v["rot_3"]], dtype=np.float32)
            
            SH_C0 = 0.28209479177387814
            color = np.array([
                0.5 + SH_C0 * v["f_dc_0"],
                0.5 + SH_C0 * v["f_dc_1"],
                0.5 + SH_C0 * v["f_dc_2"],
                1 / (1 + np.exp(-v["opacity"]))
            ])
            
            buffer.write(position.tobytes())
            buffer.write(scales.tobytes())
            buffer.write((color * 255).clip(0, 255).astype(np.uint8).tobytes())
            buffer.write(
                ((rot / np.linalg.norm(rot)) * 128 + 128)
                .clip(0, 255)
                .astype(np.uint8)
                .tobytes()
            )
        
        return buffer.getvalue()

    def process_ply_file(self, ply_path):
        """Read PLY file and convert to SPLAT format"""
        if not os.path.exists(ply_path):
            raise FileNotFoundError(f"PLY file not found: {ply_path}")
            
        plydata = PlyData.read(ply_path)
        return self.process_ply_data(plydata)

    def set_ply(self, data):
        """Accept either PLY file path or pre-processed SPLAT data"""
        if isinstance(data, str):
            # It's a file path
            self.splat_data = self.process_ply_file(data)
        else:
            # It's pre-processed SPLAT data
            self.splat_data = data
            
        # Update hash and timestamp
        self.data_hash = hashlib.md5(self.splat_data).hexdigest()
        self.last_modified = time.time()