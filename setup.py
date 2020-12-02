from setuptools import setup

setup(
    name="beacon_data_importer",
    version="2.0",
    packages=["beacon"],
    install_requires=[
        "click==7.1",
        "petl==1.6.8",
    ],
    entry_points="""
      [console_scripts]
      beacon=beacon.cli:main
    """,
)
