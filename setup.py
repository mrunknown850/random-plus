from setuptools import setup, find_packages

setup(
    name="RandomPlusPlus",
    version="0.1.2",
    description="An interpreter for Random+ (.rnd)",
    author="MrUnknown850",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "random-plus = src:interpret"
        ]
    }   
)