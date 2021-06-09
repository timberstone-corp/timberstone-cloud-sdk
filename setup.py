import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timberstone-cloud-sdk",  # Replace with your own username
    version="0.0.7",
    author="Marcelo Ventura",
    author_email="marceloventura@outlook.com",
    description="A pyhton pulumi sdk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timberstone-corp/timberstone-cloud-sdk",
    packages=setuptools.find_packages(exclude=['tests*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
