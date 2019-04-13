from titlecase import titlecase


class CannotValidate(Exception):
    pass


class ValidationDoesNotExist(Exception):
    pass


def check_mandatory_tags(tags, mandatory_tags):
    missing_tags = []
    for k in mandatory_tags:
        if k not in tags:
            missing_tags.append(k)
    return len(missing_tags) == 0, missing_tags


def check_mime_type(mime_type, valid_mime_types):
    valid_mime_type = mime_type in valid_mime_types
    error = None
    if not valid_mime_type:
        error = (
            f"{mime_type} mime type is not accepted according to your configuration."
        )
    return valid_mime_type, error


def check_bitrate(bitrate, minimum_bitrate):
    is_valid = True
    # Not all inputs formats have a bitrate property in Mutagen
    if bitrate is not None:
        is_valid = bitrate >= minimum_bitrate
    error = None
    if not is_valid:
        error = f"{str(bitrate)} bitrate is below the minimum bitrate of {str(minimum_bitrate)}"
    return is_valid, error


def check_enrichment_success(enrichments, expected_enrichments):
    missing_enrichments = []
    for k in expected_enrichments:
        if enrichments.get(k, {}).get("best_match") is None:
            missing_enrichments.append(k)
    return len(missing_enrichments) == 0, missing_enrichments


def check_output_filename_template():
    pass


def check_capitalization(tags, tags_to_capitalize):
    errors = []
    for t in tags_to_capitalize:
        try:
            assert tags.get(t) == titlecase(tags.get(t, ""))
        except AssertionError:
            errors.append(t)
    return len(errors) == 0, errors


AVAILABLE_VALIDATIONS = {
    "mandatory_tags": {
        "func": check_mandatory_tags,
        "object_to_check": "tags",
        "error_key": "missing_tags",
    },
    "accepted_input_mime_types": {
        "func": check_mime_type,
        "object_to_check": "input_mime_type",
        "error_key": "invalid_input_mime_type",
    },
    "minimum_input_bitrate": {
        "func": check_bitrate,
        "object_to_check": "input_bitrate",
        "error_key": "low_input_bitrate",
    },
    "minimum_output_bitrate": {
        "func": check_bitrate,
        "object_to_check": "output_bitrate",
        "error_key": "low_output_bitrate",
    },
    "required_enrichments": {
        "func": check_enrichment_success,
        "object_to_check": "enrichments",
        "error_key": "missing_enrichments",
    },
}


def validate(config, **kwargs):
    validation_errors = {}
    for validation in AVAILABLE_VALIDATIONS.keys():
        if config.get(validation) is not None:
            constraint = config.get(validation)
            validation_func = AVAILABLE_VALIDATIONS[validation]["func"]
            error_key = AVAILABLE_VALIDATIONS[validation]["error_key"]
            object_to_check = AVAILABLE_VALIDATIONS[validation]["object_to_check"]
            try:
                is_valid, errors = validation_func(kwargs[object_to_check], constraint)
                if not is_valid:
                    validation_errors[error_key] = errors
            except KeyError:
                raise CannotValidate(
                    f"Cannot validate {validation} because {object_to_check} was not provided to the validator."
                )

    global_valid = not bool(validation_errors)
    return global_valid, validation_errors
