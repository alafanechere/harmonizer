from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="harmonizer",
    version="0.1.3",
    package_data={"": ["logme.ini"]},
    description="Harmonizes your audio media: converts, normalizes, enriches and validates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Editors",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
    ],
    url="http://github.com/alafanechere/harmonizer",
    author="Augustin Lafanechere",
    author_email="augustin.lafanechere@gmail.com",
    license="GPLv3+",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "eyeD3==0.8.10",
        "pydub==0.23.1",
        "pyacoustid==1.1.5",
        "mutagen==1.42.0",
        "discogs-client==2.2.2",
        "spotipy==2.4.4",
        "titlecase==0.12.0",
        "click==7.0",
        "pyyaml==5.1",
        "logme==1.3.2",
        "schema==0.7.0",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    include_package_data=True,
    entry_points={"console_scripts": ["harmonizer=harmonizer.cli:harmonize_directory"]},
    zip_safe=False,
)
