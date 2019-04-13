import pytest
import schema
from harmonizer import config


@pytest.fixture
def valid_config():
    return {
        "output_bitrate": 192,
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def bad_bitrate_config():
    return {
        "output_bitrate": 191,
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def bad_enrichments_config():
    return {
        "output_bitrate": 192,
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "deezer": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def bad_required_enrichments_config():
    return {
        "output_bitrate": 320,
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "deezer"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def bad_mime_types_enrichments_config():
    return {
        "output_bitrate": 128,
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/wav", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def missing_mandatory_config():
    return {
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def unexisting_validation_config():
    return {
        "output_bitrate": 192,
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_togs": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def invalid_min_max_bitrate():
    return {
        "output_bitrate": 192,
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 190,
        },
    }


@pytest.fixture
def valid_config_with_optional():
    return {
        "output_bitrate": 192,
        "normalization_headroom": 0.2,
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def normalization_headroom_too_high():
    return {
        "output_bitrate": 192,
        "normalization_headroom": {"active": True, "normalization_headroom": "1.2"},
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def normalization_headroom_bad_float():
    return {
        "output_bitrate": 192,
        "normalization_headroom": {"active": True, "normalization_headroom": 0.01},
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


@pytest.fixture
def normalization_headroom_bad_type():
    return {
        "output_bitrate": 192,
        "normalization_headroom": 20,
        "enrichments": {
            "discogs": {"discogs_token": "xxx"},
            "spotify": {"sp_client_id": "xxx", "sp_client_secret": "xxx"},
        },
        "validations": {
            "mandatory_tags": ["artist", "album", "title"],
            "accepted_input_mime_types": ["audio/mp3", "audio/flac", "audio/mp4"],
            "required_enrichments": ["discogs", "spotify"],
            "minimum_input_bitrate": 192,
        },
    }


def test_valid_config(valid_config):
    parsed_config = config.parse(valid_config)
    assert isinstance(parsed_config, dict)
    assert parsed_config.get("normalization_headroom") == 0.1


def test_wrong_optional(
    normalization_headroom_bad_type,
    normalization_headroom_too_high,
    normalization_headroom_bad_float,
):
    expected_error = "Normalization headroom should be between 0.1 and 0.9 with a single digit decimal."

    with pytest.raises(schema.SchemaError) as excinfo:
        config.parse(normalization_headroom_bad_type)
    assert expected_error in str(excinfo.value)

    with pytest.raises(schema.SchemaError) as excinfo:
        config.parse(normalization_headroom_too_high)
    assert expected_error in str(excinfo.value)

    with pytest.raises(schema.SchemaError) as excinfo:
        config.parse(normalization_headroom_bad_float)
    assert expected_error in str(excinfo.value)


def test_valid_config_optional(valid_config_with_optional):
    parsed_config = config.parse(valid_config_with_optional)
    assert parsed_config.get("normalization_headroom") == 0.2

    valid_config_with_optional.pop("normalization_headroom")
    parsed_config = config.parse(valid_config_with_optional)
    assert parsed_config.get("normalization_headroom", {}) == 0.1


def test_bad_bitrate_config(bad_bitrate_config):
    with pytest.raises(schema.SchemaError) as excinfo:
        config.parse(bad_bitrate_config)
    assert "Output bit rate must be 128, 192 or 320" in str(excinfo.value)


def test_bad_required_enrichments_config(bad_required_enrichments_config):
    with pytest.raises(schema.SchemaError) as excinfo:
        config.parse(bad_required_enrichments_config)
    assert "This required enrichment is not supported" in str(excinfo.value)


def test_bad_mime_types_config(bad_mime_types_enrichments_config):
    with pytest.raises(schema.SchemaError) as excinfo:
        config.parse(bad_mime_types_enrichments_config)
    assert (
        "One of the accepted_input_mime_types you defined is not supported as input."
        in str(excinfo.value)
    )


def test_missing_mandatory_config(missing_mandatory_config):
    with pytest.raises(schema.SchemaError) as excinfo:
        config.parse(missing_mandatory_config)

    assert "Missing key: 'output_bitrate'" in str(excinfo.value)


def test_unexisting_validation_config(unexisting_validation_config):
    with pytest.raises(schema.SchemaError) as excinfo:
        config.parse(unexisting_validation_config)
    assert "Wrong key 'mandatory_togs'" in str(excinfo.value)


def test_invalid_min_bitrate(invalid_min_max_bitrate):
    with pytest.raises(schema.SchemaError) as excinfo:
        config.parse(invalid_min_max_bitrate)
    assert "The minimum_input_bitrate is not 320, 192 or 128" in str(excinfo.value)
