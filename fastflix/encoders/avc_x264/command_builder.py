# -*- coding: utf-8 -*-
import re
import secrets

from fastflix.encoders.common.helpers import Command, generate_all, null, generate_color_details
from fastflix.models.encode import x264Settings
from fastflix.models.fastflix import FastFlix


def build(fastflix: FastFlix):
    settings: x264Settings = fastflix.current_video.video_settings.video_encoder_settings

    beginning, ending = generate_all(fastflix, "libx264")

    beginning += f'{f"-tune {settings.tune}" if settings.tune else ""} ' f"{generate_color_details(fastflix)} "

    if settings.profile and settings.profile != "default":
        beginning += f"-profile {settings.profile} "

    pass_log_file = fastflix.current_video.work_path / f"pass_log_file_{secrets.token_hex(10)}.log"

    if settings.bitrate:
        command_1 = (
            f"{beginning} -pass 1 "
            f'-passlogfile "{pass_log_file}" -b:v {settings.bitrate} -preset {settings.preset} {settings.extra if settings.extra_both_passes else ""} -an -sn -dn -f mp4 {null}'
        )
        command_2 = (
            f'{beginning} -pass 2 -passlogfile "{pass_log_file}" '
            f"-b:v {settings.bitrate} -preset {settings.preset} {settings.extra} "
        ) + ending
        return [
            Command(
                re.sub("[ ]+", " ", command_1), ["ffmpeg", "output"], False, name="First pass bitrate", exe="ffmpeg"
            ),
            Command(
                re.sub("[ ]+", " ", command_2), ["ffmpeg", "output"], False, name="Second pass bitrate", exe="ffmpeg"
            ),
        ]

    elif settings.crf:
        command = f"{beginning} -crf {settings.crf} " f"-preset {settings.preset} {settings.extra} {ending}"
        return [
            Command(re.sub("[ ]+", " ", command), ["ffmpeg", "output"], False, name="Single pass CRF", exe="ffmpeg")
        ]

    else:
        return []
