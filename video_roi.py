from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, \
    QFileDialog, QMessageBox, QSlider
from PyQt5.QtCore import Qt, pyqtSignal
import pyqtgraph as pg
import numpy as np
import imageio as io
import os
from glob import glob
import flammkuchen as fl
import json

class ImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Interface(QWidget):
    curImChanged = pyqtSignal(int)

    def __init__(self, fn):
        super().__init__()
        self.l = QGridLayout(self)
        self.fn = fn
        self.roi_fn = self.fn.replace(".mp4",".roi")

        # self.ims = fl.load(self.fn)['segmentation']
        self.ims = io.mimread(self.fn, memtest=False)

        self.rois = {}

        self.im = ImageView()
        self.l.addWidget(self.im)

        self.zSlider = QSlider(Qt.Horizontal)
        self.zSlider.setMinimum(0)
        self.zSlider.setMaximum(len(self.ims)-1)
        self.zSlider.valueChanged.connect(self.changeZ)
        self.l.addWidget(self.zSlider)

        self.roi = pg.RectROI((100, 100), (200, 300), pen="r")
        self.roi.sigRegionChangeFinished.connect(self.saveROI)
        self.im.addItem(self.roi)

        self.curIm = 0
        self.init_im()

    def changeZ(self):
        self.curIm = self.zSlider.value()
        self.curImChanged.emit(self.curIm)
        self.init_im()

    def init_im(self):
        im = self.ims[self.curIm]
        
        if len(im.shape) == 2:
            im = im.transpose(1, 0)
        elif len(im.shape) == 3:
            im = im.transpose(1, 0, 2)
        else:
            pass

        self.im.setImage(im)

        if os.path.exists(self.roi_fn):
            with open(self.roi_fn) as fp:
                roi_ = json.load(fp)
                self.roi.setPos(roi_['pos'])
                self.roi.setSize(roi_['size'])

    def saveROI(self):
        pos = self.roi.pos().x(), self.roi.pos().y()  # x, y
        size = self.roi.size().x(), self.roi.size().y()  # w, h

        with open(self.roi_fn, "w+") as fp:
            json.dump({
                    'pos': pos,
                    'size': size,
                }, fp, indent=4)

    def keyPressEvent(self, e):
        modifiers = QApplication.keyboardModifiers()

        if e.key() == Qt.Key_D:
            self.zSlider.setValue(self.zSlider.value()+1)

        elif e.key() == Qt.Key_A:
            self.zSlider.setValue(self.zSlider.value()-1)


        # e.key() == Qt.Key_X
        # modifiers == Qt.ControlModifier

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.status = self.statusBar()
        self.menu = self.menuBar()

        # Main top menu
        self.file = self.menu.addMenu("&File")
        self.file.addAction("Open", self.open)
        self.file.addAction("Save", self.save)
        self.file.addAction("Close", self.close)

        # Central widget
        self.w = None

        # Title
        self.setWindowTitle("ROI selector")
        self.setGeometry(100, 100, 800, 600)

    def open(self):
        self.fn = QFileDialog.getOpenFileName(filter="*.mp4;*.avi")[0]

        if self.fn:
            self.status.showMessage(self.fn)
            self.w = Interface(self.fn)
            self.setCentralWidget(self.w)
            self.w.curImChanged.connect(self.showCurIm)

    def showCurIm(self, ix):
        self.status.showMessage(self.fn+"   [{}]".format(ix))

    def save(self):
        QMessageBox.information(self, 
            "Data saved.", 
            "Data is automatically saved when the ROI is changed in a given image.")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    m = Main()
    m.show()

    sys.exit(app.exec_())