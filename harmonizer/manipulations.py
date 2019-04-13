import mimetypes
import os

import acoustid
import eyed3
import mutagen
import pydub
from titlecase import titlecase


def load_audio(local_audio_path):
    return pydub.AudioSegment.from_file(local_audio_path)


def normalize(sound, headroom=0.1):
    normalized = pydub.effects.normalize(sound, headroom)
    change_in_dbfs = sound.dBFS - normalized.dBFS
    return sound.dBFS, normalized.dBFS, change_in_dbfs, normalized


def export(sound, output_path, audio_format="mp3", bitrate=192, tags={}):
    sound.export(
        output_path, format=audio_format, bitrate=str(bitrate) + "k", tags=tags
    )
    return audio_format, bitrate, output_path


def fingerprint(local_normalized_path):
    duration, fp_encoded = acoustid.fingerprint_file(local_normalized_path)
    return duration, fp_encoded.decode("utf8")


def extract_file_metadata(local_path):
    mime_type = None
    tags = {}
    mutagen_file = mutagen.File(local_path, easy=True)
    if mutagen_file is not None:
        mime_type = mutagen_file.mime[0]
        if mutagen_file.tags is not None:
            tags = {k: ", ".join(v) for k, v in dict(mutagen_file.tags).items()}
    return mime_type, tags


def get_cover_art(file_path, image_output_dir):
    audio = mutagen.File(file_path)
    raw_bytes = None
    if audio is not None:
        for t in ["covr", "APIC:cover", "APIC:"]:
            if t in audio:
                try:
                    raw_bytes = audio[t].data
                    mime_type = audio[t].mime
                except AttributeError:
                    raw_bytes = None
        if raw_bytes is not None:
            image_output_path = os.path.basename(file_path)
            image_output_name, _ = os.path.splitext(image_output_path)
            if mime_type in ["image/jpeg", "image/jpg"]:
                ext = ".jpeg"
            else:
                ext = mimetypes.guess_extension(mime_type)
            image_output_path = os.path.join(image_output_dir, image_output_name + ext)
            with open(image_output_path, "wb") as f:
                f.write(raw_bytes)
            return image_output_path


def capitalize_tags(tags, tags_to_capitalize=["artist", "album", "title"]):
    for t in tags_to_capitalize:
        original = tags.get(t)
        if original is not None:
            tags[t] = titlecase(original)
    return tags


def get_mp3_bitrate(local_file_path):
    audio = eyed3.load(local_file_path)
    if audio is not None:
        bitrate = audio.info.mp3_header.bit_rate
        if audio.info.mp3_header.mode == "Mono":
            bitrate = bitrate * 2
        return bitrate


def pipeline(
    local_audio_path,
    audio_output_path,
    image_output_dir,
    output_audio_format="mp3",
    active_normalize=False,
    normalization_headroom=0.1,
    target_bitrate=192,
    capitalized_tags=True,
):
    mime_type, tags = extract_file_metadata(local_audio_path)

    original_bitrate = get_mp3_bitrate(local_audio_path)
    cover_art_path = get_cover_art(local_audio_path, image_output_dir)
    if capitalized_tags:
        tags = capitalize_tags(tags)
    sound = load_audio(local_audio_path)
    if active_normalize:
        original_dbfs, normalized_dbfs, change_in_dbfs, sound = normalize(
            sound, normalization_headroom
        )
        normalization_meta = {
            "change_dbfs": change_in_dbfs,
            "normalized_dbfs": normalized_dbfs,
            "original_dbfs": original_dbfs,
        }

    else:
        normalization_meta = {}

    output_audio_format, output_bitrate, exported_audio_path = export(
        sound, audio_output_path, output_audio_format, target_bitrate, tags
    )
    duration, fp = fingerprint(exported_audio_path)

    return (
        {
            "normalization": normalization_meta,
            "tags": tags,
            "has_cover_art": cover_art_path is not None,
            "fingerprinting": {"duration": duration, "fingerprint": fp},
            "mime_type": mime_type,
            "original_bitrate": original_bitrate,
            "export": {"audio_format": output_audio_format, "bitrate": output_bitrate},
        },
        exported_audio_path,
        cover_art_path,
    )
