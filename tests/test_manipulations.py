import os
import base64
from glob import glob

import eyed3
import pydub
import pytest
from titlecase import titlecase

from harmonizer import manipulations


@pytest.fixture
def mp3_sample():
    return pydub.AudioSegment.from_mp3("tests/audio_samples/inputs/test1.mp3")


@pytest.fixture
def mp3_with_cover():
    return "tests/audio_samples/inputs/with_cover.mp3"


@pytest.fixture
def mp3_without_cover():
    return "tests/audio_samples/inputs/test1.mp3"


@pytest.fixture
def normalized_path():
    sound = pydub.AudioSegment.from_file("tests/audio_samples/inputs/test1.mp3")
    return manipulations.export(sound, "tests/audio_samples/outputs/normalized.mp3")[2]


@pytest.fixture
def id3_files():
    return glob("tests/audio_samples/inputs/with_tags*")


@pytest.fixture
def low_bitrate_mp3s():
    return [
        "tests/audio_samples/inputs/64k.mp3",
        "tests/audio_samples/inputs/128k.mp3",
        "tests/audio_samples/inputs/test1.mp3",
    ]


@pytest.fixture
def high_bitrate_mp3s():
    return ["tests/audio_samples/inputs/320k.mp3"]


@pytest.fixture
def not_mp3s():
    return ["tests/audio_samples/inputs/format_test.m4a"]


@pytest.fixture
def various_samples():
    io = []
    for s in os.listdir("tests/audio_samples/inputs"):
        i = os.path.join("tests/audio_samples/inputs", s)
        basename, ext = os.path.splitext(s)
        if ext in [".mp3", ".flac", ".m4a", ".wav"]:
            o = os.path.join("tests/audio_samples/outputs", f"{basename}.mp3")
            io.append((i, o, "tests/image_outputs"))
    return io


def test_normalize(mp3_sample):
    expected_original_dbfs = mp3_sample.dBFS
    original_dbfs, new_dbfs, change_in_dbfs, _ = manipulations.normalize(mp3_sample)
    assert new_dbfs != original_dbfs
    assert expected_original_dbfs == original_dbfs
    assert change_in_dbfs


def test_load_audio(various_samples):
    for s_in, _, _ in various_samples:
        sound = manipulations.load_audio(s_in)
        assert sound.duration_seconds > 0


def test_fingerprint(normalized_path):
    duration, fingerprint = manipulations.fingerprint(normalized_path)
    assert duration > 0
    assert isinstance(fingerprint, str)
    os.remove(normalized_path)


def test_extract_file_metadata(id3_files):
    mandatory_tag_keys = ["artist", "title", "album"]
    for f in id3_files:
        mime_type, id3_meta = manipulations.extract_file_metadata(f)
        assert isinstance(id3_meta, dict)
        assert mime_type.startswith("audio/")
        assert all([k in id3_meta for k in mandatory_tag_keys])


def test_bitrate(low_bitrate_mp3s, not_mp3s, high_bitrate_mp3s):
    for f in low_bitrate_mp3s:
        original_bitrate = manipulations.get_mp3_bitrate(f)
        assert isinstance(original_bitrate, int)
        assert original_bitrate < 192

    for f in high_bitrate_mp3s:
        original_bitrate = manipulations.get_mp3_bitrate(f)
        assert isinstance(original_bitrate, int)
        assert original_bitrate >= 192

    original_bitrate = manipulations.get_mp3_bitrate(not_mp3s[0])
    assert original_bitrate is None


def test_full_manip(various_samples):
    for s_in, s_out, _ in various_samples:
        sound = manipulations.load_audio(s_in)
        original_dbfs, new_dbfs, change_in_dbfs, normalized_sound = manipulations.normalize(
            sound
        )
        assert original_dbfs == sound.dBFS
        assert new_dbfs != sound.dBFS
        assert change_in_dbfs

        audio_format, bitrate, output_path = manipulations.export(
            normalized_sound, s_out
        )
        assert audio_format == "mp3"
        assert bitrate == "192k"
        _, ext = os.path.splitext(output_path)
        assert ext == ".mp3"
        exported_sound = eyed3.load(output_path)
        bitrate = exported_sound.info.bit_rate[1]
        assert bitrate == 192
        os.remove(output_path)


@pytest.fixture
def expected_manipulations_keys():
    return [
        "normalization",
        "fingerprinting",
        "export",
        "tags",
        "mime_type",
        "original_bitrate",
        "has_cover_art",
    ]


@pytest.fixture
def expected_normalization_keys():
    return ["original_dbfs", "normalized_dbfs", "change_dbfs"]


@pytest.fixture
def expected_fingerprinting_keys():
    return ["fingerprint", "duration"]


@pytest.fixture
def expected_export_keys():
    return ["audio_format", "bitrate"]


def test_audio_manipulation_pipeline(
    various_samples,
    expected_manipulations_keys,
    expected_normalization_keys,
    expected_fingerprinting_keys,
    expected_export_keys,
):
    for s_in, s_out, image_output_dir in various_samples:
        manipulation_result, exported_filepath, exported_image_path = manipulations.pipeline(
            s_in, s_out, image_output_dir, active_normalize=True
        )
        assert exported_filepath == s_out
        assert isinstance(manipulation_result, dict)
        assert all([k in manipulation_result for k in expected_manipulations_keys])
        assert all(
            [
                k in manipulation_result["normalization"]
                for k in expected_normalization_keys
            ]
        )

        assert all(
            [
                k in manipulation_result["fingerprinting"]
                for k in expected_fingerprinting_keys
            ]
        )

        assert all([k in manipulation_result["export"] for k in expected_export_keys])
        # os.remove(s_out)


def test_capitalize_tags():
    tags = {
        "artist": "the beatles",
        "album": "Sgt. Peppers",
        "title": "Lucy in the sky with diamond",
    }
    results = manipulations.capitalize_tags(tags.copy())
    assert results == {k: titlecase(v) for k, v in tags.items()}


def test_get_covert_art(mp3_with_cover, mp3_without_cover):
    cover_art_path = manipulations.get_cover_art(mp3_with_cover, "tests/image_outputs")
    assert os.path.exists(cover_art_path)

    cover_art_path = manipulations.get_cover_art(
        mp3_without_cover, "tests/image_outputs"
    )
    assert cover_art_path is None
