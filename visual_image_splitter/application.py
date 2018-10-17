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

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

from visual_image_splitter.argument_parser import parse_arguments
import visual_image_splitter.logger
import visual_image_splitter.ui.main_window
import visual_image_splitter.model.model

logger = visual_image_splitter.logger.get_logger("Application")


class Application(QApplication):

    def __init__(self, argv: typing.List[str]=sys.argv):

        super(Application, self).__init__(argv)
        self.args = parse_arguments()
        visual_image_splitter.logger.configure_root_logger(self.args)
        logger.info("Starting visual_image_splitter")
        self.model: visual_image_splitter.model.model.Model = visual_image_splitter.model.model.Model(self.args, self)
        self.main_window = visual_image_splitter.ui.main_window.MainWindow(self.model)
        self.main_window.show()
        logger.debug("Initialisation done. Starting event loop.")
        self.exec_()
        logger.debug("Left event loop.")

    @pyqtSlot()
    def shutdown(self):
        logger.info("About to exit.")
        self.closeAllWindows()
        self.model.worker_thread.requestInterruption()
        logger.debug("Requested worker thread to interrupt it’s work.")
        self.model.worker_thread.quit()
        logger.debug("Requested worker thread to quit. Waiting for it to finish.")
        self.model.worker_thread.wait()
        logger.info("Worker thread finished. Exiting…")
        self.quit()

    def get_currently_edited_image(self):
        return self.main_window.opened_images_list_view.currentIndex()
