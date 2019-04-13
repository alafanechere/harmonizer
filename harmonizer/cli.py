import json
import os
import time
from glob import glob
import sys

import click
import logme
import schema
import yaml

from harmonizer import config, enrichments, manipulations, validations


@click.command(
    help="Please provide an audio_input_dir path and an audio_output_dir path to launch harmonization of your files."
)
@click.argument(
    "audio_input_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.argument(
    "audio_output_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.argument(
    "conf",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    envvar="HARMONIZER_CONF",
)
@click.option(
    "--json-out",
    "json_output_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to directory to which  JSON metadata will be written to.",
)
@click.option(
    "--img-out",
    "image_output_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to directory to which extracted cover arts will be written to.",
)
@logme.log(name="Harmonizer CLI")
def harmonize_directory(
    audio_input_dir,
    audio_output_dir,
    conf,
    json_output_dir,
    image_output_dir,
    logger=None,
):
    if json_output_dir is None:
        json_output_dir = audio_output_dir
    if image_output_dir is None:
        image_output_dir = audio_output_dir

    with open(conf, "r") as f:
        try:
            raw_config = yaml.load(f, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            logger.error(
                "Cannot read your YAML config. File does not seems valid: ", exc
            )
            sys.exit(1)
    try:
        parsed_config = config.parse(raw_config)
    except schema.SchemaError as e:
        for error in e.errors:
            if error is not None:
                logger.error(error)
        logger.error(
            "Could not parse the config, it does not have the expected schema."
        )
        sys.exit(1)

    valid_extensions = [
        "*." + m.replace("audio/", "")
        for m in parsed_config.get("validations", {}).get(
            "accepted_input_mime_types", []
        )
    ]
    globs = [os.path.join(audio_input_dir, ext) for ext in valid_extensions]

    for file_type in globs:
        for f in glob(file_type):
            start_time = time.time()
            results = harmonize_file(
                f, audio_output_dir, json_output_dir, image_output_dir, parsed_config
            )
            process_time = time.time() - start_time
            f = os.path.basename(f)
            if len(results["validation_errors"]) > 0:
                logger.warning(
                    f"Validation error for {f}: {results['validation_errors']}"
                )
            logger.info(
                f"Successfully processed file {f} in {int(process_time)} seconds."
            )


def harmonize_file(
    local_file_path, audio_output_dir, json_output_dir, image_output_dir, parsed_config
):
    enrichment_creds = {}
    for e in parsed_config["enrichments"].values():
        enrichment_creds.update(e)

    basename = os.path.basename(local_file_path)
    basename, _ = os.path.splitext(basename)
    output_file_path = os.path.join(audio_output_dir, basename) + ".mp3"
    output_result_path = os.path.join(json_output_dir, basename) + ".json"
    manipulation_metadata, exported_filepath, cover_art_path = manipulations.pipeline(
        local_file_path,
        output_file_path,
        image_output_dir,
        active_normalize=parsed_config["normalization_headroom"] > 0,
        normalization_headroom=parsed_config["normalization_headroom"],
    )

    if "tags" in manipulation_metadata:
        enrichments_metadata = enrichments.pipeline(
            manipulation_metadata["tags"],
            list(parsed_config.get("enrichments", {}).keys()),
            **enrichment_creds,
        )
    else:
        enrichments_metadata = {}

    is_valid, validations_metadata = validations.validate(
        parsed_config.get("validations", {}),
        tags=manipulation_metadata.get("tags"),
        output_bitrate=manipulation_metadata["export"].get("output_bitrate"),
        input_bitrate=manipulation_metadata.get("original_bitrate"),
        input_mime_type=manipulation_metadata.get("mime_type"),
        enrichments=enrichments_metadata,
    )

    results = {
        "output_file_path": output_file_path,
        "validation_errors": validations_metadata,
        "enrichments_metadata": enrichments_metadata,
        "manipulation_metadata": manipulation_metadata,
    }

    with open(output_result_path, "w") as f:
        json.dump(results, f)
    return results


if __name__ == "__main__":
    harmonize_directory()
