# BAGLS ROI Annotation

Use `bagls_roi.py` to annotate each frame in the BAGLS training and test dataset.
By changing an ROI (size and position!), the ROI is automatically saved as JSON *.roi file.

For video or segmentation, use `video_roi.py` and `segmentation_roi.py` instead.

## Required libraries

* pyqtgraph
* PyQt5
* numpy
* imageio
* flammkuchen

## Shortcuts for `bagls_roi.py`

- D: Next Frame
- A: Previous Frame
- P: Find next, not annotated frame
