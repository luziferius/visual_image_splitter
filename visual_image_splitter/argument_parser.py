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

import argparse

import visual_image_splitter.visual_image_splitter


def generate_argument_parser() -> argparse.ArgumentParser:
    """Generates and returns an ArgumentParser instance."""
    description = "This program takes pictures and cuts them into pieces. It can be used to split scanned images " \
                  "containing multiple images into the individual parts."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "images",
        nargs="*",
        metavar="IMAGE",
        help="One or more image files. The given files will be loaded on program start. Specifying images here is "
             "optional, as additional images can be loaded at runtime later."
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"visual_image_splitter Version {visual_image_splitter.visual_image_splitter.__version__}"
    )
    parser.add_argument(
        "-V", "--verbose",
        action="store_true",
        help="Increase output verbosity. Also show debug messages on the standard output."
    )
    parser.add_argument(
        "--cutelog-integration",
        action="store_true",
        help="Connect to a running cutelog instance with default settings to display the full program log."
    )
    return parser


def parse_arguments():
    parser = generate_argument_parser()
    return parser.parse_args()
