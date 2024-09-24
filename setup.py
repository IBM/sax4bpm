import sys
from setuptools import setup, find_packages

def parse_requirements(filename):
    try:
        with open(filename, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []
    
with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()

install_requires = parse_requirements("requirements.txt")

setup(
    name="sax4bpm", 
    version='{{VERSION_PLACEHOLDER}}', 
    author="Inna Skarbovsky",
    author_email="inna@il.ibm.com",
    description="Open source Python library for deriving explanations about business processes based on process,causal and XAI perspectives",
    long_description=long_description,
    license='GPL 3.0',
    long_description_content_type="text/markdown",
    url="https://github.com/IBM/sax4bpm",
    packages=find_packages(include=['sax', 'sax.*']),    
    python_requires='>=3.9',
    install_requires=install_requires,
    include_package_data=True,
)
