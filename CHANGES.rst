Changelog
=========

Version 0.3.1 (11.04.2019)
--------------------------

- Fixed GUI issues when opening images, if no other images are already opened.
  Now the selection list panel on the right will stay empty and not display
  garbage until an image is activated on the left.
- Fixed GUI issues when all images are closed using the Save All button.
  Now the selection editor and the selection list are properly emptied during the save operation.


Version 0.3.0 (20.11.2018)
--------------------------

- Implemented selection rendering in the right panel.
- Improved internal code quality.


Version 0.2.0 (17.10.2018)
--------------------------

- Implemented better image rendering for the opened images list.
  Images are now displayed as a list, keeping the aspect ratio of shown images.
- Improved internal code quality.


Version 0.1.0 (02.10.2018)
--------------------------
The first working version implements the basic image splitting functionality.

Output images are each stored alongside the corresponding input file,
by appending an underscore separated, five-digit, zero-filled running number to the file name, before the file type
ending.


Implemented features
++++++++++++++++++++

- Add advanced selection presets as command line parameters. Those are applied as selections to all loaded image files.
- Open images using command line parameters and by using a file chooser dialog window at runtime.
- Display images with selection rectangles in a central selection editor
- Drawing selections on a per-file basis
- Closing images without saving. This discards all selections added.
- Saving current selections for single images and for all images at once.
  This extracts the selections and saves them as separate files alongside the input files.
- Long running IO operations are executed in the background. (Currently without progress notifications.)
