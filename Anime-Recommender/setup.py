from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="Anime-Recommender",
    version="1.0.0",
    author="Sagar",
    packages=find_packages(),
    install_requires = requirements
)

# Anime-Recommender setup script - to run this script, use the command:
# pip install -e .