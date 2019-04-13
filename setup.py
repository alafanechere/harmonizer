from setuptools import setup

setup(name="harmonizer",
      version="0.1",
      description="Harmonize your audio media, converts, normalize, enrich with metadata",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis"
        "Topic :: Multimedia :: Sound/Audio :: Editors"
        "Topic :: Multimedia :: Sound/Audio :: Conversion"
      ],
      url="http://github.com/alafanechere/harmonizer",
      author="Augustin Lafanechere",
      author_email="augustin.lafanechere@gmail.com",
      license="GPLv3+",
      packages=["harmonizer"],
      install_requires=["eyed3",
                        "pydub",
                        "pyacoustid",
                        "mutagen",
                        "discogs-client",
                        "spotipy",
                        "titlecase",
                        "click",
                        "pyyaml",
                        "logme",
                        "schema"],
        setup_requires=["pytest-runner"],
      tests_require=["pytest"],
      include_package_data=True,
      entry_points={
          "console_scripts": ["harmonizer=harmonizer.cli:harmonize_directory"],
      },
      zip_safe=False)
