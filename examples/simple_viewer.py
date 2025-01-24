from gaussian_viewer import GaussianViewer
from gaussian_viewer._splat_writer import write_splat_data
from plyfile import PlyData
import numpy as np
from io import BytesIO
import os

def process_ply_to_splat(ply_path) -> bytes:
    """Convert PLY file to SPLAT format"""
    # Read PLY file
    plydata = PlyData.read(ply_path)
    xyz = np.stack((np.asarray(plydata.elements[0]["x"]),
                    np.asarray(plydata.elements[0]["y"]),
                    np.asarray(plydata.elements[0]["z"])), axis=1).astype(np.float32)
    opacities = np.asarray(plydata.elements[0]["opacity"], dtype=np.float32)

    features_dc = np.stack([
        np.asarray(plydata.elements[0]["f_dc_0"]),
        np.asarray(plydata.elements[0]["f_dc_1"]),
        np.asarray(plydata.elements[0]["f_dc_2"])
    ], axis=1).astype(np.float32)

    scales = np.stack([
        np.asarray(plydata.elements[0]["scale_0"]),
        np.asarray(plydata.elements[0]["scale_1"]),
        np.asarray(plydata.elements[0]["scale_2"])
    ], axis=1).astype(np.float32)

    rots = np.stack([
        np.asarray(plydata.elements[0]["rot_0"]),
        np.asarray(plydata.elements[0]["rot_1"]),
        np.asarray(plydata.elements[0]["rot_2"]),
        np.asarray(plydata.elements[0]["rot_3"])
    ], axis=1).astype(np.float32)

    sorted_indices = np.argsort(
        -np.exp(scales[:, 0] + scales[:, 1] + scales[:, 2])
        / (1 + np.exp(-opacities))
    )

    # Pre-allocate buffer
    total_bytes = len(sorted_indices) * (12 + 12 + 4 + 4)
    buffer = BytesIO(bytearray(total_bytes))
    
    # Call C function with numpy arrays
    write_splat_data(buffer, sorted_indices, xyz, scales, features_dc, opacities, rots)

    return buffer.getvalue()


def main():
    current_path = os.path.dirname(os.path.abspath(__file__))
    ply0_path = os.path.join(current_path, 'gaussian_137.ply')
    ply1_path = os.path.join(current_path, 'gaussian_1194.ply')
    splat_data0 = process_ply_to_splat(ply0_path)
    splat_data1 = process_ply_to_splat(ply1_path)
    print('ply data processed')

    viewer = GaussianViewer(port=6789)
    viewer.show(splat_data0)
    print("Viewer started")
    input("Press Enter to change PLY file")
    viewer.show(splat_data1)
    print("PLY file changed")
    input("Press Enter to exit")


if __name__ == "__main__":
    main()
