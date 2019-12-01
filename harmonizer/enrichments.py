import discogs_client as discogs_api
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class TooMuchRequests(Exception):
    pass


class InsufficientTags(Exception):
    pass


class UnavailableEnrichment(Exception):
    pass


class MissingCredentials(Exception):
    pass


ENRICHMENTS_MAPPING = {
    "discogs": {"required_tags": ["album", "artist"]},
    "spotify": {"required_tags": ["title", "artist"]},
}


def pipeline(
    track_tags,
    enrichments=["discogs", "spotify"],
    discogs_token=None,
    sp_client_id=None,
    sp_client_secret=None,
):
    results = {}
    for enrichement_name in enrichments:
        try:
            enrichment = ENRICHMENTS_MAPPING[enrichement_name]
            required_tags = enrichment["required_tags"]
            try:
                assert all([t in track_tags for t in required_tags])
            except AssertionError:
                raise InsufficientTags(
                    "The track you try to enrich is missing a tag for the enrichment you want"
                )
            if enrichement_name == "spotify":
                if not all(
                    [cred is not None for cred in (sp_client_id, sp_client_secret)]
                ):
                    raise MissingCredentials(
                        "You need to provide sp_client_id and sp_client_secret for Spotify enrichment"
                    )
                best_match, other_results = spotify_enrich(
                    track_tags["title"],
                    track_tags["artist"],
                    sp_client_id,
                    sp_client_secret,
                    album=track_tags.get("album"),
                )
            elif enrichement_name == "discogs":
                if discogs_token is None:
                    raise MissingCredentials(
                        "You need to provide a discogs token for Discogs enrichment"
                    )
                best_match, other_results = discogs_enrich(
                    track_tags["artist"], track_tags["album"], discogs_token
                )
            else:
                raise UnavailableEnrichment(
                    "The enrichment you tried to use does not exist"
                )
            results[enrichement_name] = {
                "best_match": best_match,
                "other_results": other_results,
            }
        except KeyError:
            raise UnavailableEnrichment(
                "The enrichment you tried to use does not exist"
            )
    return results


def discogs_enrich(artist, album, discogs_token, client_user_agent="ingestion"):
    discogs_client = discogs_api.Client(client_user_agent, user_token=discogs_token)

    try:
        results = discogs_client.search(f"{artist} {album}", type="release")
        results = [r.data for r in results.page(1)]
    except discogs_api.exceptions.HTTPError as e:
        if hasattr(e, "message") and "too quickly" in e.message:
            raise TooMuchRequests("You're making too much requests to discogs")
        else:
            raise (e)

    if results:
        same_artist_names = [
            r
            for r in results
            if r.get("artists", [{"name": ""}])[0]["name"].lower() == artist.lower()
        ]
        if same_artist_names:
            results = same_artist_names

        same_album_names = [
            r
            for r in results
            if r.get("title").lower() == f"{artist.lower()} - {album.lower()}"
        ]
        if same_album_names:
            results = same_album_names

        with_images = [r for r in results if len(r.get("cover_image", "")) > 0]
        if with_images:
            results = with_images

        vinyls = [r for r in results if r["format"][0].lower() == "vinyl"]
        if vinyls:
            results = vinyls

        community_sorted = sorted(
            results, key=lambda x: x["community"]["want"], reverse=True
        )

        return community_sorted[0], community_sorted
    else:
        return None, []


def spotify_enrich(title, artist, sp_client_id, sp_client_secret, album=None):
    client_credentials_manager = SpotifyClientCredentials(
        client_id=sp_client_id, client_secret=sp_client_secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    title = title.split("(")[0]
    queries = []
    if album is not None:
        queries.append(f"album:{album} artist:{artist} track:{title}".lower())
    queries.append(f"artist:{artist} track:{title}".lower())

    for q in queries:
        results = sp.search(q=q, type="track", limit=20)
        tracks = results["tracks"]["items"]
        if tracks:
            return tracks[0], tracks
    return None, []
