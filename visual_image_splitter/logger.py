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

import logging
import logging.handlers
import sys

root_logger = logging.getLogger("visual_image_splitter")
LOG_FORMAT = "%(asctime)s %(levelname)s - %(name)s - %(message)s"


def get_logger(name: str) -> logging.Logger:
    return root_logger.getChild(name)


def configure_root_logger(args):
    """Initialise logging system"""
    logger = logging.getLogger()
    logger.setLevel(1)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    if args.cutelog_integration:
        socket_handler = logging.handlers.SocketHandler("127.0.0.1", 19996)  # default listening address
        logger.addHandler(socket_handler)
        logger.info(f"""Connected logger "{logger.name}" to local log server.""")
