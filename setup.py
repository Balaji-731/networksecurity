from setuptools import find_packages,setup
from typing import List

def get_requirements(file_path: str) -> List[str]:
    """Reads the requirements from a file and returns them as a list."""
    requirements_list: List[str] = []
    try:  
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                requirements=line.strip()
                if requirements and not requirements.startswith('-e .'):
                    requirements_list.append(requirements)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")

    return requirements_list

setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Balaji",
    author_email="poralabalaji@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)