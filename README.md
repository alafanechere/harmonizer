# HARMONIZER
[![PyPI version](https://badge.fury.io/py/harmonizer.svg)](https://badge.fury.io/py/harmonizer)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/harmonizer.svg)

This library helps you to **convert**, **normalize**, **enrich** and **validate** your music library.
It fullfills the need we have at [imr.party](https://imr.party) to harmonize the music library of our webradio.

The library comes shipped with a CLI tools which allow you to process audio files in a directory to create normalized mp3 versions of all files, enrich their metadata from various sources (Discogs, Spotify).

## What it does
* **Audio conversion**: Converts FLAC, MP3, AAC (m4a) to MP3 (128k, 192k, 320k).
* **Audio normalization**: Peak normalize your input audio. Normalization is expressed in headroom ratio (0.1 means max peak will me 90% of the maximum volume).
* **Metadata extraction** : 
    * Audio tags:  extracted from the audio and written to the JSON metadata results.
    * Audio fingerprinting: [Chromaprint](https://acoustid.org/chromaprint) fingerprinting extracted from the audio and written to the JSON metadata results. 
* **Metadata enrichment**:
    * Use Discogs API to find the releases related to the audio track. Get your tokens [here](https://www.discogs.com/developers/)
    * Use Spotify API to find the audio track in their catalog. Get your API secrets [here](https://developer.spotify.com/documentation/web-api/)
* **Covert Art extraction (MP3 only)** : extract the covert art to an image file.
* **Validation** : run various integrity check to assert the input audio respects the rules you defined in the your config.
    * Minimum input bit rate (MP3 only)
    * Mandatory audio tags
    * Accepted input mime types
    

## Outputs
All file processing will create 2 or 3 files :
* The mp3 converted and normalized audio version of the input audio file.
* A metadata json file (check [metadata_output.json](./examples/metadata_output.json))
* A cover art image file if present in the original file

## Install
### System dependency

**ffmpeg**:\
OS X : `$ brew install ffmpeg`\
Linux: `$ sudo apt install ffmpeg`

**libmagic**:\
OS X : `$ brew install libmagic`\
Linux: `$ sudo apt install libmagic-dev`

**fpcalc**: \
Install [Chromaprint](https://acoustid.org/chromaprint) and add the executable to your path.

### Pip
`$ pip install harmonizer`

## CLI usage
```bash
Usage: cli.py [OPTIONS] AUDIO_INPUT_DIR AUDIO_OUTPUT_DIR CONF

  Please provide an audio_input_dir path and an audio_output_dir path to
  launch harmonization of your files.

Options:
  --json-out DIRECTORY  Path to directory to which  JSON metadata will be
                        written to.
  --img-out DIRECTORY   Path to directory to which extracted cover arts will
                        be written to.
  --help                Show this message and exit.

```
## Config file structure
Checkout [example_config.yml](./example_config.yml).

## Test
`$ python setup.py test`

## TODO:
* Docstrings
* More documentation
* Better discogs search and match algorithm
* More pipeline control through the config
