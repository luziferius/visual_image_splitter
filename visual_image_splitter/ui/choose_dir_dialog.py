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

from PyQt5 import QtWidgets

from visual_image_splitter.logger import get_logger
logger = get_logger(__name__)
del get_logger


class OutputDirDialog(QtWidgets.QFileDialog):
    """
    This Dialog is used to choose an output directory to write files to.
    """

    def __init__(self, parent: QtWidgets.QWidget = None):
        super(OutputDirDialog, self).__init__(parent, "Choose output directory")
        self.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)  # Only allow directory selection.
        logger.info("Created OutputDirDialog instance.")
