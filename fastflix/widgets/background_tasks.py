#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from subprocess import PIPE, STDOUT, run

from qtpy import QtCore

from fastflix.language import t

logger = logging.getLogger("fastflix")

__all__ = ["ThumbnailCreator"]


class ThumbnailCreator(QtCore.QThread):
    def __init__(self, main, command=""):
        super().__init__(main)
        self.main = main
        self.command = command

    def run(self):
        self.main.thread_logging_signal.emit(f"INFO:{t('Generating thumbnail')}: {self.command}")
        result = run(self.command, stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True)
        if result.returncode > 0:
            if "No such filter: 'zscale'" in result.stdout.decode(encoding="utf-8", errors="ignore"):
                self.main.thread_logging_signal.emit(
                    "ERROR:Could not generate thumbnail because you are using an outdated FFmpeg! "
                    "Please use FFmpeg 4.3+ built against the latest zimg libraries. "
                    "Static builds available at https://ffmpeg.org/download.html "
                    "(Linux distributions are often slow to update)"
                )
            else:
                self.main.thread_logging_signal.emit(f"ERROR:{t('Could not generate thumbnail')}: {result.stdout}")

            self.main.thumbnail_complete.emit(0)
        else:
            self.main.thumbnail_complete.emit(1)


class SubtitleFix(QtCore.QThread):
    def __init__(self, main, mkv_prop_edit, video_path):
        super().__init__(main)
        self.main = main
        self.mkv_prop_edit = mkv_prop_edit
        self.video_path = video_path

    def run(self):
        output_file = str(self.video_path).replace("\\", "/")
        self.main.thread_logging_signal.emit(f'INFO:{t("Will fix first subtitle track to not be default")}')
        try:
            result = run(
                [self.mkv_prop_edit, output_file, "--edit", "track:s1", "--set", "flag-default=0"],
                stdout=PIPE,
                stderr=STDOUT,
            )
        except Exception as err:
            self.main.thread_logging_signal.emit(f'ERROR:{t("Could not fix first subtitle track")} - {err}')
        else:
            if result.returncode != 0:
                self.main.thread_logging_signal.emit(
                    f'WARNING:{t("Could not fix first subtitle track")}: {result.stdout}'
                )
