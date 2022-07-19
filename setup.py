from setuptools import setup

setup(
    name="Len of objects, with the Zed2 cam ",
    version="1.0",
    description="A demonstration of triangulation to calculate the height of electronic objects using the Zed Cam.",
    author="BRAIN (Brazilian Artificial Inteligence Nuclues)",
    license="LICENSE.txt",
    long_description=open("README.md").read(),
    install_requires=[
        "opencv-python",
        "matplotlib"
        "numpy",
    ]
)