from setuptools import find_packages, setup

setup(
    name='kg_schemas',
    version='0.1.2',
    description='Schemas definition for Art KB',
    author='Giacomo Blanco',
    author_email='giacomo.blanco@linksfoundation.com',
    packages=find_packages(),
    install_requires=[
        'pydantic==1.10.21',
    ],
    python_requires='>=3.11',
)