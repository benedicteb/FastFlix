# -*- coding: utf-8 -*-
import logging

from qtpy import QtWidgets

from fastflix.encoders.common.setting_panel import SettingPanel
from fastflix.language import t
from fastflix.models.encode import CopySettings
from fastflix.models.fastflix_app import FastFlixApp

logger = logging.getLogger("fastflix")


class Copy(SettingPanel):
    profile_name = "copy"

    def __init__(self, parent, main, app: FastFlixApp):
        super().__init__(parent, main, app)
        self.main = main
        self.app = app

        grid = QtWidgets.QGridLayout()

        grid.addWidget(QtWidgets.QLabel(t("This will just copy the video track as is.")), 0, 0)
        grid.addWidget(
            QtWidgets.QLabel(t("No crop, scale, rotation,flip nor any other filters will be applied.")), 1, 0
        )
        grid.addWidget(QtWidgets.QWidget(), 2, 0, 10, 1)
        self.setLayout(grid)
        self.hide()

    def update_video_encoder_settings(self):
        self.app.fastflix.current_video.video_settings.video_encoder_settings = CopySettings()
