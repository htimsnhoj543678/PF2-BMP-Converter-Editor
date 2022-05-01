# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from pf2_bmp import *
 
# window class
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
 
        # setting title
        self.setWindowTitle("map editor")
 
        # setting geometry for main window
        self.setGeometry(100, 100, 512, 512)

        # creating image object
        self.image = QImage(self.size(), QImage.Format_Grayscale8)

        # making image color to white
        self.image.fill(240) #240 or 0xF0

        # variables
        # drawing flag
        self.drawing = False
        # default brush size
        self.brushSize = 1
        # default color
        self.brushColor = Qt.black
 
        # QPoint object to tract the point
        self.lastPoint = QPoint()

        # creating menu bar
        mainMenu = self.menuBar()
 
        # creating file menu for save and clear action
        fileMenu = mainMenu.addMenu("File")
 
        # adding brush size to main menu
        b_size = mainMenu.addMenu("Brush Size")
 
        # adding brush color to ain menu
        b_color = mainMenu.addMenu("Brush Color")
 
        # creating save action
        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl + S")
        fileMenu.addAction(saveAction)
        saveAction.triggered.connect(self.save)

        #creating open action
        openAction = QAction("Open", self)
        fileMenu.addAction(openAction)
        openAction.triggered.connect(self.open)
 
        # creating clear action
        clearAction = QAction("Clear", self)
        clearAction.setShortcut("Ctrl + C")
        fileMenu.addAction(clearAction)
        clearAction.triggered.connect(self.clear)
 
        # creating options for brush sizes
        # creating action for selecting pixel of 1px
        pix_1 = QAction("1px", self)
        b_size.addAction(pix_1)
        pix_1.triggered.connect(self.Pixel_1)

        pix_4 = QAction("4px", self)
        b_size.addAction(pix_4)
        pix_4.triggered.connect(self.Pixel_4)
 
        pix_7 = QAction("7px", self)
        b_size.addAction(pix_7)
        pix_7.triggered.connect(self.Pixel_7)
 
        pix_9 = QAction("9px", self)
        b_size.addAction(pix_9)
        pix_9.triggered.connect(self.Pixel_9)
 
        pix_12 = QAction("12px", self)
        b_size.addAction(pix_12)
        pix_12.triggered.connect(self.Pixel_12)
 
        # creating options for brush color
        # creating action for black color
        black = QAction("Out of bounds (black)", self)
        b_color.addAction(black)
        black.triggered.connect(self.outofbounds)
 
        white = QAction("In bounds (white)", self)
        b_color.addAction(white)
        white.triggered.connect(self.inbounds)
 
    # method for checking mouse cicks
    def mousePressEvent(self, event):
 
        # if left mouse button is pressed
        if event.button() == Qt.LeftButton:
            # make drawing flag true
            self.drawing = True
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.lastPoint = event.pos()
            painter.drawPoint(self.lastPoint)
            self.update()
 
    # method for tracking mouse activity
    def mouseMoveEvent(self, event):
         
        # checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()
 
    # method for mouse left button release
    def mouseReleaseEvent(self, event):
 
        if event.button() == Qt.LeftButton:
            # make drawing flag false
            self.drawing = False
 
    # paint event
    def paintEvent(self, event):
        # create a canvas
        canvasPainter = QPainter(self)
         
        # draw rectangle  on the canvas
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

    # method for saving canvas
    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files(*.bmp)")
 
        if filePath == "":
            return

        image = self.image.convertToFormat(QImage.Format_Grayscale8)
        rotated = image.transformed(QTransform().rotate(90))

        buffer = []
        pixel_map=[[0 for row in range(0,512)] for col in range(0,512)]

        for i in range(0, 512):
            for j in range(0, 512):
                pixColor = qGray(rotated.pixel(i, j))
                buffer.append(pixColor.to_bytes(1, "little"))

        elem = itertools.cycle(buffer)	

        for i in range(0, 512):
            for j in range(0, 512):
                pixel_map[i][j]= next(elem)
        
        write_bitmap(filePath, pixel_map)               #Step2: save your modified .bmp

    # method for opening a file to edit
    def open(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files(*.bmp)")
        colortable =[]
        
        if filePath == "":
            return

        pixmap = QPixmap()
        pixmap.load(filePath)
        self.image = pixmap.toImage()

        for c in range(256):
            colortable.append(qRgb(c,c,c))
        
        self.image.setColorTable(colortable)

    # method for clearing every thing on canvas
    def clear(self):
        # make the whole canvas white
        white = QColor(240, 240, 240).rgb()
        self.image.fill(white)
        # update
        self.update()
 
    # methods for changing pixel sizes
    def Pixel_1(self):
        self.brushSize = 1

    def Pixel_4(self):
        self.brushSize = 4
 
    def Pixel_7(self):
        self.brushSize = 7
 
    def Pixel_9(self):
        self.brushSize = 9
 
    def Pixel_12(self):
        self.brushSize = 12
 
    # methods for changing brush color
    def outofbounds(self):
        self.brushColor = Qt.black
 
    def inbounds(self):
        white = QColor(240, 240, 240)
        self.brushColor = white

class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
 
# create pyqt5 app
App = QApplication(sys.argv)
 
# create the instance of our Window
window = Window()
 
# showing the window
window.show()
 
# start the app
sys.exit(App.exec())