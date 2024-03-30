from setuptools import setup, find_packages

setup(
    name='goitneo_python_project',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'address-book=goitneo_python_project.main:main',
        ],
    }
)