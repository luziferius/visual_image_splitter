# Copyright (C) 2018 Thomas Hess <thomas.hess@udo.edu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import pathlib
import functools

from PyQt5.QtCore import QFile, QSize, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QLabel
from PyQt5 import uic
from PyQt5.QtSvg import QSvgRenderer

from ._logger import get_logger
logger = get_logger("common")

try:
    import visual_image_splitter.ui.compiled_resources
except ModuleNotFoundError:
    import warnings
    # No compiled resource module found. Load bare files from disk instead.
    warn_msg = "Compiled Qt resources file not found. If visual_image_splitter is launched directly from the source " \
               "directory, this is expected and harmless. If not, this indicates a failure in the resource compilation."
    warnings.warn(warn_msg)
    RESOURCE_PATH_PREFIX = str(pathlib.Path(__file__).resolve().parent.parent / "resources")
    local_path = pathlib.Path(__file__).resolve().parent.parent.parent / "files"
    if local_path.exists():
        # This is running from the source directory, thus icons are in <root>/files
        ICON_PATH_PREFIX = str(local_path)
    else:
        # This is an installation. Icons reside in visual_image_splitter/resources/icons,
        # where they were copied by setup.py
        ICON_PATH_PREFIX = str(pathlib.Path(__file__).resolve().parent.parent / "resources" / "icons")
    del local_path
else:
    import atexit
    # Compiled resources found, so use it.
    RESOURCE_PATH_PREFIX = ":"
    ICON_PATH_PREFIX = ":/icons"
    atexit.register(visual_image_splitter.ui.compiled_resources.qCleanupResources)


def set_url_label(label: QLabel, path: pathlib.Path):

    url = QUrl.fromLocalFile(str(path.expanduser()))
    if not label.openExternalLinks():
        # The openExternalLinks property is not set in the UI file, so fail fast instead of doing workarounds.
        raise ValueError(
            f"QLabel with disabled openExternalLinks property used to display an external URL. This won’t work, so "
            f"fail now. Label: {label}, Text: {label.text()}")
    label.setText(f"""<a href="{url.toString():s}">{path:s}</a>""")


@functools.lru_cache()
def load_icon(name: str) -> QIcon:
    file_path = ICON_PATH_PREFIX + "/" + name
    icon = QIcon(file_path)
    if not icon.availableSizes() and file_path.endswith(".svg"):
        # FIXME: Work around Qt Bug: https://bugreports.qt.io/browse/QTBUG-63187
        # Manually render the SVG to some common icon sizes.
        icon = QIcon()  # Discard the bugged QIcon
        renderer = QSvgRenderer(file_path)
        for size in (16, 22, 24, 32, 64, 128):
            pixmap = QPixmap(QSize(size, size))
            pixmap.fill(QColor(255, 255, 255, 0))
            renderer.render(QPainter(pixmap))
            icon.addPixmap(pixmap)
    return icon


def _get_ui_qfile(name: str):
    """
    Returns an opened, read-only QFile for the given QtDesigner UI file name. Expects a plain name like "main_window".
    The file ending and resource path is added automatically.
    Raises FileNotFoundError, if the given ui file does not exist.
    :param name:
    :return:
    """
    file_path = f"{RESOURCE_PATH_PREFIX}/ui/{name}.ui"
    file = QFile(file_path)
    if not file.exists():
        error_message = f"UI file not found: {file_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message)
    file.open(QFile.ReadOnly)
    return file


def load_ui_from_file(name: str):
    """
    Returns a tuple from uic.loadUiType(), loading the ui file with the given name.
    :param name:
    :return:
    """
    ui_file = _get_ui_qfile(name)
    try:
        base_type = uic.loadUiType(ui_file, from_imports=True)
    finally:
        ui_file.close()
    return base_type


"""
This renamed function is supposed to be used during class definition to make the intention clear.
Usage example:

class SomeWidget(*inherits_from_ui_file_with_name("SomeWidgetUiFileName")):
    def __init__(self, parent):
        super(SomeWidget, self).__init__(parent)
        self.setupUi(self)


"""
inherits_from_ui_file_with_name = load_ui_from_file
