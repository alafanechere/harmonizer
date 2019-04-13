import pytest
from harmonizer import validations


def test_check_mandatory_tags():
    mandatory_tags = ["artist", "album"]
    tags = {"artist": "yolo", "album": "yolo"}
    is_valid, errors = validations.check_mandatory_tags(tags, mandatory_tags)
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)
    assert is_valid
    assert len(errors) == 0

    mandatory_tags = ["artist", "album"]
    tags = {"album": "yolo"}
    is_valid, errors = validations.check_mandatory_tags(tags, mandatory_tags)
    assert is_valid == False
    assert len(errors) == 1

    mandatory_tags = ["artist", "album", "title"]
    tags = {"album": "yolo"}
    is_valid, errors = validations.check_mandatory_tags(tags, mandatory_tags)
    assert not is_valid
    assert len(errors) == 2


def test_check_mime_type():
    valid_mime_types = ["audio/mp3", "audio/mp4"]
    is_valid, error = validations.check_mime_type("audio/mp3", valid_mime_types)
    assert is_valid
    assert error is None

    is_valid, error = validations.check_mime_type("audio/mp2", valid_mime_types)
    assert not is_valid
    assert (
        error == "audio/mp2 mime type is not accepted according to your configuration."
    )


def test_check_bitrate():
    min_br = 192
    is_valid, error = validations.check_bitrate(190, min_br)
    assert not is_valid
    assert error == "190 bitrate is below the minimum bitrate of 192"
    is_valid, error = validations.check_bitrate(192, min_br)
    assert is_valid
    assert error is None

    is_valid, error = validations.check_bitrate(193, min_br)
    assert is_valid
    assert error is None


def test_enrichment_success():
    enrichments = {"discogs": {"best_match": "foor", "other_results": ["bar"]}}
    required_enrichments = ["discogs"]
    is_valid, errors = validations.check_enrichment_success(
        enrichments, required_enrichments
    )
    assert is_valid
    assert errors == []
    enrichments = {"discogs": {"best_match": "foor", "other_results": ["bar"]}}
    required_enrichments = ["spotify"]
    is_valid, errors = validations.check_enrichment_success(
        enrichments, required_enrichments
    )
    assert not is_valid
    assert errors == ["spotify"]

    enrichments = {
        "discogs": {"best_match": "foor", "other_results": ["bar"]},
        "spotify": {"best_match": "foor", "other_results": ["bar"]},
    }
    required_enrichments = ["spotify"]
    is_valid, errors = validations.check_enrichment_success(
        enrichments, required_enrichments
    )
    assert is_valid
    assert errors == []

    enrichments = {"discogs": {"best_match": None, "other_results": ["bar"]}}
    required_enrichments = ["discogs"]
    is_valid, errors = validations.check_enrichment_success(
        enrichments, required_enrichments
    )
    assert not is_valid
    assert errors == ["discogs"]


def test_check_capitalization():
    tags_to_capitalize = ["title", "artist"]
    valid_tags = {"title": "Hey Jude", "artist": "The Beatles"}
    is_valid, errors = validations.check_capitalization(valid_tags, tags_to_capitalize)
    assert is_valid
    assert len(errors) == 0

    invalid_tags = {"title": "hey jude", "artist": "The beatles"}
    is_valid, errors = validations.check_capitalization(
        invalid_tags, tags_to_capitalize
    )
    assert not is_valid
    assert len(errors) == 2


@pytest.fixture
def config():
    return {
        "mandatory_tags": ["artist", "album", "title"],
        "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
        "required_enrichments": ["discogs", "spotify"],
        "minimum_input_bitrate": 192,
        "minimum_output_bitrate": 192,
    }


def test_validate(config):
    object_to_validate = {
        "input_mime_type": "audio/mp3",
        "tags": {"artist": "foo", "title": "baar", "album": "baar"},
        "input_bitrate": 192,
        "output_bitrate": 192,
        "enrichments": {
            "discogs": {"best_match": {"toto": "toto"}},
            "spotify": {"best_match": {"toto": "toto"}},
        },
    }

    is_valid, validation_errors = validations.validate(config, **object_to_validate)
    assert is_valid
    assert validation_errors == {}


def test_validate_missing_object(config):
    object_to_validate = {"input_mime_type": "audio/mp3"}
    with pytest.raises(validations.CannotValidate) as excinfo:
        validations.validate(config, **object_to_validate)
    assert "Cannot validate" in str(excinfo.value)


def test_validate_bad_input(config):
    object_to_validate = {
        "input_mime_type": "audio/mp12",
        "tags": {"artist": "foo", "title": "baar"},
        "input_bitrate": 190,
        "output_bitrate": 190,
        "enrichments": {
            "discogs": {"best_match": None},
            "spotify": {"best_match": None},
        },
    }

    is_valid, validation_errors = validations.validate(config, **object_to_validate)
    assert not is_valid

    assert (
        validation_errors["invalid_input_mime_type"]
        == "audio/mp12 mime type is not accepted according to your configuration."
    )
    assert validation_errors["missing_tags"] == ["album"]
    assert (
        validation_errors["low_input_bitrate"]
        == "190 bitrate is below the minimum bitrate of 192"
    )
    assert (
        validation_errors["low_output_bitrate"]
        == "190 bitrate is below the minimum bitrate of 192"
    )
    assert validation_errors["missing_enrichments"] == ["discogs", "spotify"]
