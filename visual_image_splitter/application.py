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

import sys
import typing

from PyQt5.QtWidgets import QApplication, QMainWindow

from visual_image_splitter.argument_parser import parse_arguments
import visual_image_splitter.logger
import visual_image_splitter.ui.main_window


class Application(QApplication):

    def __init__(self, argv: typing.List[str]=sys.argv):

        super(Application, self).__init__(argv)
        self.args = parse_arguments()
        visual_image_splitter.logger.configure_root_logger(self.args)
        self.main_window: QMainWindow = visual_image_splitter.ui.main_window.MainWindow()
        self.main_window.show()
        self.exec_()
