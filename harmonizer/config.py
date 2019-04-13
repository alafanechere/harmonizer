from schema import Schema, Optional, And


HANDLED_MIME_TYPES = ["audio/mp3", "audio/mpeg", "audio/flac", "audio/mp4", "audio/m4a"]
HANDLED_ENRICHMENTS = ["discogs", "spotify"]
HANDLED_BITRATES = [320, 192, 128]
HANDLED_MANDATORY_TAGS = [
    "title",
    "artist",
    "album",
    "date",
    "genre",
    "tracknumber",
    "discnumber",
    "albumartist",
]

DEFAULT_NORMALIZATION_HEADROOM = 0.1

CONFIG_SCHEMA = Schema(
    {
        "output_bitrate": And(
            lambda x: x in HANDLED_BITRATES,
            error="Output bit rate must be 128, 192 or 320",
        ),
        Optional("enrichments"): {
            Optional(
                "discogs",
                error="You must provide a discogs API token for this enrichment",
            ): {"discogs_token": str},
            Optional(
                "spotify",
                error="You must provide a spotify client id and secret for this enrichment",
            ): {"sp_client_id": str, "sp_client_secret": str},
        },
        Optional("validations"): {
            Optional(
                "mandatory_tags", error="This mandatory tag is not supported"
            ): lambda mfs: all([x in HANDLED_MANDATORY_TAGS for x in mfs]),
            Optional("accepted_input_mime_types"): And(
                lambda accepted_mime_types: all(
                    [x in HANDLED_MIME_TYPES for x in accepted_mime_types]
                ),
                error="One of the accepted_input_mime_types you defined is not supported as input.",
            ),
            Optional("minimum_input_bitrate"): And(
                int,
                lambda x: x in HANDLED_BITRATES,
                error="The minimum_input_bitrate is not 320, 192 or 128",
            ),
            Optional("required_enrichments"): And(
                lambda required_enrichments: all(
                    [x in HANDLED_ENRICHMENTS for x in required_enrichments]
                ),
                error="This required enrichment is not supported.",
            ),
        },
        Optional("normalization_headroom", default=0.1): And(
            lambda x: x in [float("0." + str(i)) for i in range(1, 10)],
            error="Normalization headroom should be between 0.1 and 0.9 with a single digit decimal.",
        ),
    }
)


def parse(raw_config):
    return CONFIG_SCHEMA.validate(raw_config)
