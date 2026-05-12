from setuptools import find_packages, setup


setup(
    name="pbr-atlas",
    version="0.1.0",
    description="B1 differentiable PBR baking-error atlas sanity code",
    packages=find_packages(include=["pbr_atlas", "pbr_atlas.*"]),
    python_requires=">=3.10",
)

