GUI
===

Left panel
----------

- Properly render Image items.
- Delegate content:
    - Undistorted, small image preview
    - File path or file name
    - Selection count
    - Output path
- Editor content:
    - Output path
    - Reset button
    - Close button
- Accept image file drops

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

Model
=====
