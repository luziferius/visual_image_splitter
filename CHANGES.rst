Changelog
=========

Version 0.1.0 (07.09.2018)
--------------------------
The first working version implements the basic functionality.
Implemented features:

- Add advanced selection presets as command line parameters. Those are applied to all loaded image files.
- Open images using command line parameters and by using a dialog window at runtime
- Display images with selection rectangles in a central selection editor
- Drawing selections on a per-file basis
- Closing images without saving. This discards all selections added.
- Saving current selections for single images and for all images at once.
  This extracts the selections and saves them as separate files alongside the input files.
- Long running IO operations are executed in the background. (Currently without progress notifications.)
