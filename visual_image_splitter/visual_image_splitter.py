#!/usr/bin/env python3
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

import visual_image_splitter.application

# These constants are extracted by setup.py
PROGRAMNAME = "visual_image_splitter"
VERSION = "0.1.0"
COPYRIGHT = "(C) 2018 Thomas Hess"
AUTHOR = "Thomas Hess"
AUTHOR_EMAIL = "thomas.hess@udo.edu"
MAINTAINER = "Thomas Hess"
MAINTAINER_EMAIL = "thomas.hess@udo.edu"
HOME_PAGE = "https://github.com/luziferius/visual_image_splitter"

_app = None


def main():
    global _app
    _app = visual_image_splitter.application.Application()


if __name__ == "__main__": 
    main()
