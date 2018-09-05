Model
=====

- Implement re-ordering selections
- Implement setting custom output directories for files
- Properly implement the QT Model API.
- Deleting selections for files
- Lossless mode for JFIF files (.jpeg), using the `jpegtran` tool.

GUI
===

- Make the main window panels resizable.
- i18n and l10n
- Provide an editor for preset selections, to edit the selection presets given on the command line.
    - Allow adding, editing and removing presets.



Left panel
----------

- Properly render Image items.
- UI Delegate content:
    - Undistorted, small image preview
    - File path or file name
    - Selection count
    - Output path
- Editor content:
    - Output path
    - Reset button
    - Close button
- Accept image file drops to open new files


Middle panel
------------

- Scale the loaded image to fill the middle panel, retaining the aspect ratio.
- Right click context menu, if clicked on a selection. Allow to delete one of the
  items below. Maybe add other actions?
- Selection movement view/tool:
    - If activated, switch to movement mode
    - Allow to drag and drop move selections around
    - Resize, by dragging the border or corner?
- Selection reorder mode?
    - Re-order all selections by clicking them one after another?
- Render selection numbers inside the selections, if the number fits?

Right panel
-----------

- Render all selections for the active image
- Delegate content:
    - Undistorted, small selection preview
    - Selection rectangle (x, y, width, height)
    - Index number
    - Resulting file name?
- Editor content:
    - Output path?
    - Selection coordinates
- Drag and drop selection re-ordering.

Menu
----

- Default selection editor: Maybe a dialog window?
    - Allows to add, edit and remove default selections
    - Added selections are applied to all open images
- About window
- AboutQt dialog
