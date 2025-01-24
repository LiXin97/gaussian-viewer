from setuptools import setup, find_packages, Extension
import numpy as np

setup(
    name="gaussian-viewer",
    version="0.1.0",
    author="Xin Li",
    author_email="lixin.1997.lixin@gmail.com",
    description="A lightweight WebGL-based viewer for 3D Gaussian Splatting models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LiXin97/gaussian-viewer",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "websockets",
        "numpy",
        "plyfile",
    ],
    package_data={
        'gaussian_viewer': ['web/*'],
    },
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    ext_modules=[
        Extension(
            "gaussian_viewer._splat_writer",
            ["gaussian_viewer/_splat_writer.c"],
            include_dirs=[np.get_include()]
        )
    ]
)
