Visual Image Splitter
=====================

This program allows to split large picture files into their individual parts.

If you use flatbed scanners to scan small photos, cards, negatives or similar pieces
and place more than one piece on the scanner bed at a time to reduce scanning time and device wear,
you end up having large image files containing multiple items.

Those images need to be split into their parts for individual processing.
Advanced image manipulation programs, such as The GIMP often miss a way to perform this splitting task
without much tedium. Such programs can often only perform a single crop operation at a time, requiring many repetitive
steps to perform a multi-image split.

`Visual Image Splitter` performs this splitting task with as few repetitive steps as possible.
You can load all your scanned image files at once. In each file, draw as many selection rectangles as needed, and then
extract them all at once.

Requirements
------------

- Python 3.6
- PyQt5

Install
-------

Install the latest version from the source repository: **python3 setup.py install**

Usage
-----

Execute *visual_image_splitter* to start the program and show the main window.

Command line arguments
++++++++++++++++++++++

Visual Image splitter accepts some command line switches:

- s, --selection: Adds a pre-defined selection to all image files loaded. This argument can be specified more than once to add multiple selections.
    - It takes four arguments (optional parts in square brackets): [-]x1[%] [-]y1[%] [+-]x2[%] [+-]y2[%]
    - If any value is specified with a percent sign, it is treated as a decimal percentage of the actual image size it will be applied to.
    - The first two values, x1 and y1, build the first anchor point. Values are relative to the top and left image border. If a value is negative, it is treated as relative to the right and bottom image border.
    - The second two values, x2 and y2 form the second anchor point. If a sign is given (either positive or negative), the value is treated as relative to the `first anchor point`.
- List of image files
    - visual_image_splitter accepts a list of image files as positional arguments. These image files will be loaded on program start.

Command line examples
+++++++++++++++++++++
TODO.

User interface
++++++++++++++

The area on the left side shows the list of the currently opened images. Selecting one image opens it for selection editing.
The middle area is the selection editor. It shows the currently selected image, displays all selections for that file and allows drawing new selections.

About
-----
Visual Image Splitter is licensed under the GNU GENERAL PUBLIC LICENSE Version 3.
See the LICENSE file for details.
