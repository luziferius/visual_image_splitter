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

import typing
import pathlib

from PyQt5.QtCore import QObject

from .rectangle import Rectangle
from .image import Image
from ._logger import get_logger

logger = get_logger("model")


class Model(QObject):

    def __init__(self, args, parent: QObject=None):
        """

        :param args: Parsed command line arguments. Expects an argparse.Namespace object
        :param parent: Optional parent object
        """
        super(Model, self).__init__(parent)
        self.args = args
        logger.info(f"Creating Model instance. Arguments: {args}")
        # The predefined selections is a list of selections given on the command line. These selections are
        # automatically added to each Image file
        logger.info("Loading selections given on the command line")
        self.predefined_selections: typing.List[Rectangle] = []
        self._create_command_line_defined_selections()
        # Load all given images
        logger.info("Loading images given on the command line")
        self.images: typing.List[Image] = []
        self._open_command_line_given_images()

    def _create_command_line_defined_selections(self):
        pass

    def _open_command_line_given_images(self):
        for image_path_str in self.args.images:
            image_path = pathlib.Path(image_path_str).expanduser()
            logger.debug(f"Create Image instance with Path: '{image_path}'")
            self.open_image(image_path)

    def open_image(self, path: pathlib.Path):
        image = Image(path, self)
        logger.debug(f"Image instance created. Adding predefined selections as given on the command line: "
                     f"{self.predefined_selections}")
        for selection in self.predefined_selections:
            image.add_selection(selection)
        self.images.append(image)
