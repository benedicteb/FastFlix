# -*- coding: utf-8 -*-
import re
import secrets

from fastflix.encoders.common.helpers import Command, generate_all, null, generate_color_details
from fastflix.models.encode import AOMAV1Settings
from fastflix.models.fastflix import FastFlix


def build(fastflix: FastFlix):
    settings: AOMAV1Settings = fastflix.current_video.video_settings.video_encoder_settings
    beginning, ending = generate_all(fastflix, "libaom-av1")

    beginning += (
        "-strict experimental "
        f"-cpu-used {settings.cpu_used} "
        f"-tile-rows {settings.tile_rows} "
        f"-tile-columns {settings.tile_columns} "
        f"-usage {settings.usage} "
        f"{generate_color_details(fastflix)} "
    )

    if settings.row_mt.lower() == "enabled":
        beginning += f"-row-mt 1 "

    beginning = re.sub("[ ]+", " ", beginning)

    if settings.bitrate:
        pass_log_file = fastflix.current_video.work_path / f"pass_log_file_{secrets.token_hex(10)}.log"
        command_1 = f'{beginning} -passlogfile "{pass_log_file}" -b:v {settings.bitrate} -pass 1 {settings.extra if settings.extra_both_passes else ""} -an -f matroska {null}'
        command_2 = (
            f'{beginning} -passlogfile "{pass_log_file}" -b:v {settings.bitrate} -pass 2 {settings.extra} {ending}'
        )
        return [
            Command(command_1, ["ffmpeg", "output"], False, name="First Pass bitrate"),
            Command(command_2, ["ffmpeg", "output"], False, name="Second Pass bitrate"),
        ]
    elif settings.crf:
        command_1 = f"{beginning} -b:v 0 -crf {settings.crf} {settings.extra} {ending}"
        return [Command(command_1, ["ffmpeg", "output"], False, name="Single Pass CRF")]
