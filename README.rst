Visual Image Splitter
=====================

This program allows to split large picture files into their individual parts.

If you use flatbed scanners to scan small photos, cards, negatives or similar pieces
and place more than one piece on the scanner bed at a time to reduce scanning time and device wear,
you end up having large image files containing multiple items.

Those images may need to be split into their parts for individual processing, depending on your workflow.
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
    - Requires the PyQt5 SVG module, if it is not already bundled with your PyQt5 install. (On Ubuntu, this is in a separate package.)
    - Requires the ``pyrcc5`` command line PyQt5 resource compiler during the installation process.


Ubuntu
++++++

Install all dependencies using this command:

    ``sudo apt install python3-pyqt5 python3-pyqt5.qtsvg pyqt5-dev-tools``



Installation
------------

Clone the repository using git or download a ZIP archive snapshot from the GitHub releases page.
Install the downloaded version from the source repository root directory using: :code:`pip3 install .` (Note the trailing dot indicating the path to the repository checkout.)
Alternatively, use the program directly from the source checkout without an installation.


Usage
-----

Execute ``visual_image_splitter`` to start the program and show the main window.

Execution from the source tree without installing
+++++++++++++++++++++++++++++++++++++++++++++++++

Visual Image Splitter can be launched from the source tree:
Either use the runner script :code:`visual_image_splitter-runner.py` in the repository root directory or execute the Python source package using :code:`python3 -m visual_image_splitter`.
Both variants support command line arguments, like the installed version.


Command line arguments
++++++++++++++++++++++

Visual Image splitter accepts some command line switches:

- ``-s``, ``--selection``: Adds a selection preset to all image files loaded. This argument can be specified more than once to add multiple selection presets.
    - This switch takes exactly four numerical arguments (optional parts in square brackets): ``[-]x1[%] [-]y1[%] [+-]x2[%] [+-]y2[%]``
    - The given presets will be added as selections to *each* opened file, both to image specified on the command line *and* any image opened later.
    - If any argument value is specified with a percent sign, it is treated as a decimal percentage of the actual image size it will be applied to. Otherwise, without a percent sign, it denotes an absolute value in pixels.
    - The first value pair, ``x1`` and ``y1``, build the first anchor point. Values are relative to the top and left image border. If a value is negative, it is treated as relative to the right and bottom image border.
    - The second value pair, ``x2`` and ``y2`` form the second anchor point. If a sign is given (either positive or negative), the value is treated as relative to the `first anchor point`.
- ``-h``, ``--help``: Print the help text on the standard output
- ``-v``, ``--version``: Print the application version on the standard output
- ``-V``, ``--verbose``: Increase log output verbosity on the standard output
- ``--cutelog-integration``: Enable logging to a local network socket for external log viewing. See https://github.com/busimus/cutelog
- List of image files
    - visual_image_splitter accepts a list of image files as positional arguments. These image files will be loaded on program start.
    - The file types supported depend on the Qt library version currently in use and any file type plugin libraries accessible to Qt.
      To determine the supported formats on your system, open the program GUI once and look at the file type filter drop-down menu in the Open images dialogue window.


Command line examples
+++++++++++++++++++++

.. code-block:: console

    # Just load two PNG files on start
    visual_image_splitter a.png b.png
    # Add a selection preset. In this case, it will add a selection
    # to each loaded image that will simply crop the outer 10 pixels.
    # Because no images are specified, no images are loaded on start.
    # Use the GUI to open images.
    visual_image_splitter --selection -10 -10 10 10
    # Now, add a preset that adds a fixed 50x100 pixel selection,
    # starting relatively at 20% image width from the right and 40% from the top
    # Additionally, open all PNG files in the current directory
    visual_image_splitter -s -20% 40% +50 +100 *.png
    # Take the bottom right 10% of each opened image.
    # This starts at the bottom right corner and goes up and right for each 10%
    # of the image width and height.
    visual_image_splitter -s -0 -0 -10% -10%
    # Or, alternatively:
    visual_image_splitter -s 90% 90% 100% 100%
    # Split each image (named Scan_some_number.tiff) into 4 equal parts
    visual_image_splitter -s 0 0 50% 50% -s 0 50% 50% 100% -s 50% 0 100% 50% -s 50% 50% 100% 100% Scan_*.tiff


User interface
++++++++++++++

The area on the left side shows a list with all currently opened images. Clicking one image opens it for selection editing in the middle area.
The middle area is the selection editor. It shows the image currently selected in the image list on the left and displays all to-be extracted selections for that file.
It allows drawing new rectangular selections by dragging the mouse over the image while pressing and holding down the left mouse button.
The right area shows all selections for the currently edited image.

When adding small selections, the right area might show bad quality, low resolution preview images. This does not reflect the final extraction quality.
The downscaling is done to reduce memory usage when dealing with multiple really large source images, as high-resolution scans can be about 1GiB in size per file.
The final image extraction when clicking on the save button is performed on the unscaled source images.
Thus the final, written-to-disk result files have the same quality as the original source file.

About
-----
Visual Image Splitter is licensed under the GNU GENERAL PUBLIC LICENSE Version 3.
See the LICENSE file for details.
