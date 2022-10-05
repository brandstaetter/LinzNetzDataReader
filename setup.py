from setuptools import find_packages, setup

setup(
    name="data_analyzer",
    version="0.1",  # ignore for now
    description="Some hello world web server",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[],
    dependency_links=[],
    extras_require={},
    package_data={},
    entry_points={},
)
