import os
import time
import pytest

from harmonizer import enrichments


@pytest.fixture
def test_tracks():
    return [
        {
            "title": "Butterfly",
            "artist": "Herbie Hancock",
            "album": "Thrust",
            "expected_discogs_id": 31382,
            "expected_spotify_uri": "spotify:track:2YQBDxMbQbOsdXixdL4ZyE",
        },
        {
            "title": "Nouveau Western",
            "artist": "MC Solaar",
            "album": "Prose Combat",
            "expected_discogs_id": 1340359,
            "expected_spotify_uri": "spotify:track:4svCpwxfUDLGBa123fBDfM",
        },
        {
            "title": "Mitote",
            "artist": "cochemea",
            "album": "All my relations",
            "expected_discogs_id": 13251816,
            "expected_spotify_uri": "spotify:track:4JHlp5SIDqhgEkzEN3AU4m",
        },
        {
            "title": "Feather (ft. Cise Starr & Akin)",
            "artist": "Nujabes",
            "album": "Modal Soul",
            "expected_discogs_id": 789482,
            "expected_spotify_uri": "spotify:track:2ej1A2Ze6P2EOW7KfIosZR",
        },
    ]


@pytest.fixture
def test_tracks_not_existing():
    return [{"title": "Guy Tard", "artist": "Guy Hemaire", "album": "Le Patron"}]


@pytest.fixture
def discogs_token():
    return os.environ.get("DISCOGS_TOKEN")


@pytest.fixture
def spotify_creds():
    return {
        "sp_client_id": os.environ.get("SPOTIFY_CLIENT_ID"),
        "sp_client_secret": os.environ.get("SPOTIFY_CLIENT_SECRET"),
    }


@pytest.fixture
def all_creds():
    return {
        "discogs_token": os.environ.get("DISCOGS_TOKEN"),
        "sp_client_id": os.environ.get("SPOTIFY_CLIENT_ID"),
        "sp_client_secret": os.environ.get("SPOTIFY_CLIENT_SECRET"),
    }


@pytest.fixture
def available_enrichments():
    return ["discogs", "spotify"]


def test_mappings(available_enrichments):
    mappings = enrichments.ENRICHMENTS_MAPPING
    assert isinstance(mappings, dict)
    for e in available_enrichments:
        assert e in mappings
    for k, v in mappings.items():
        assert e in available_enrichments
        assert isinstance(v["required_tags"], list)
    expected_mapping = {
        "discogs": {"required_tags": ["album", "artist"]},
        "spotify": {"required_tags": ["title", "artist"]},
    }
    assert mappings == expected_mapping


def test_discogs_enrichment(test_tracks, discogs_token):
    for track in test_tracks:
        match, results = enrichments.discogs_enrich(
            track["artist"], track["album"], discogs_token
        )
        assert isinstance(match, dict)
        assert isinstance(results, list)
        assert all(
            match["community"]["want"] >= r["community"]["want"] for r in results
        )
        assert match["id"] == track["expected_discogs_id"]
        time.sleep(1)


def test_discogs_enrichment_no_results(test_tracks_not_existing, discogs_token):
    for track in test_tracks_not_existing:
        match, results = enrichments.discogs_enrich(
            track["artist"], track["album"], discogs_token
        )
        assert match is None
        assert results == []
        time.sleep(0.3)


def test_spotify_enrichment(test_tracks, spotify_creds):
    for track in test_tracks:
        match, results = enrichments.spotify_enrich(
            track["title"], track["artist"], **spotify_creds, album=track["album"]
        )
        assert isinstance(match, dict)
        assert isinstance(results, list)
        assert match["uri"] == track["expected_spotify_uri"]
        time.sleep(1)


def test_enrichment_pipeline(test_tracks, all_creds, available_enrichments):
    for t in test_tracks:
        results = enrichments.pipeline(t, **all_creds)
        assert all([e in results for e in available_enrichments])


def test_enrichment_pipeline_unexisting_track(
    test_tracks_not_existing, all_creds, available_enrichments
):
    results = enrichments.pipeline(test_tracks_not_existing[0], **all_creds)
    assert all([e in results for e in available_enrichments])
    for k, v in results.items():
        assert v["best_match"] == None
        assert v["other_results"] == []


def test_enrichment_pipeline_unavailable(test_tracks):
    track_tags = test_tracks[0]
    with pytest.raises(enrichments.UnavailableEnrichment) as excinfo:
        enrichments.pipeline(track_tags, ["youtube"])
    assert "does not exist" in str(excinfo.value)


def test_enrichment_pipeline_missing_creds(test_tracks):
    track_tags = test_tracks[0]
    with pytest.raises(enrichments.MissingCredentials) as excinfo:
        enrichments.pipeline(track_tags, ["discogs"])
    assert "You need to provide a discogs token" in str(excinfo.value)

    with pytest.raises(enrichments.MissingCredentials) as excinfo:
        enrichments.pipeline(track_tags, ["spotify"])
    assert "You need to provide sp_client_id and sp_client_secret" in str(excinfo.value)


def test_enrichment_pipeline_insufficient_tags(
    test_tracks, spotify_creds, discogs_token
):
    track_tags = test_tracks[0].copy()
    track_tags.pop("artist")
    with pytest.raises(enrichments.InsufficientTags) as excinfo:
        enrichments.pipeline(track_tags, ["discogs"])
    assert "missing a tag" in str(excinfo.value)

    with pytest.raises(enrichments.InsufficientTags) as excinfo:
        enrichments.pipeline(track_tags, ["spotify"])
    assert "missing a tag" in str(excinfo.value)

    with pytest.raises(enrichments.InsufficientTags) as excinfo:
        enrichments.pipeline(track_tags)
    assert "missing a tag" in str(excinfo.value)

    track_tags = test_tracks[0].copy()
    track_tags.pop("album")
    with pytest.raises(enrichments.InsufficientTags) as excinfo:
        enrichments.pipeline(track_tags, ["discogs"])
    assert "missing a tag" in str(excinfo.value)

    results = enrichments.pipeline(track_tags, enrichments=["spotify"], **spotify_creds)
    assert "spotify" in results

    track_tags = test_tracks[0].copy()
    track_tags.pop("title")
    with pytest.raises(enrichments.InsufficientTags) as excinfo:
        enrichments.pipeline(track_tags, ["spotify"])
    assert "missing a tag" in str(excinfo.value)

    results = enrichments.pipeline(
        track_tags, enrichments=["discogs"], discogs_token=discogs_token
    )
    assert "discogs" in results
