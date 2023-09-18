import sys
import libcamera
import datetime
import time
import cv2
from PyQt5.QtWidgets import QMainWindow, QApplication, QBoxLayout, QPushButton, QWidget
from PyQt5 import QtGui, QtCore, QtWidgets
from UI import *
from login import LoginPopup

# For camera
from picamera2 import Picamera2, MappedArray
from picamera2.previews.qt import QGlPicamera2

# Payment method
# import nayax.adapter as nayax

# MySQL python connector
import mysql.connector

# Css style
from style import style


# constants
colour = (0, 255, 0)
origin = (0, 30)
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thickness = 2


def apply_timestamp(request):
    timestamp = time.strftime("%Y-%m-%d %X")
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)


class NumImagePopUp(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # setting  the geometry of window
        self.setGeometry(0, 0, 400, 300)


# Main Application Window
class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # Style the window
        self.setStyleSheet(style)

        self.number_of_images = 1

        # date for file name
        self.date = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

        self.initCamera()
        # Create menu bar and add action
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu("&File")
        # fileMenu.addAction(newAction)

        self.menuBar.setVisible(False)
        # Create a flag to track if video playback is on
        self.isVideoPlayBack = False
        self.setMouseTracking(True)

        # self.showMaximized()
        self.showFullScreen()

        self.startVideoPlayback()

    # initialize camera
    def initCamera(self):
        # Create an instance of the picamera 2
        self.picam2 = Picamera2()

        # Configure the camera for preview mode
        # use libcamera to rotate the camera preview
        self.config_preview = self.picam2.create_preview_configuration(
            main={"size": (800, 600)},
            lores={"size": (640, 480)},
            transform=libcamera.Transform(hflip=1, vflip=1),
        )
        self.picam2.configure(self.config_preview)

        self.picam2.pre_callback = apply_timestamp

    def capture_done(self, job):
        # self.picam2.wait(job)
        result = self.picam2.wait(job)
        self.startDisplayImage(self.image)
        self.window.capture_button.setEnabled(True)

    def on_button_clicked(self):
        self.window.capture_button.setEnabled(False)

        # Create configuration for capturing a still image
        cfg = self.picam2.create_still_configuration(
            main={"size": (1800, 1200)}, lores={"size": (640, 480)}, display="lores"
        )
        # Calling the signal_done function ensures that the application does not block
        self.image = "/home/pi/photobooth/IMG_" + self.date + ".jpg"
        self.picam2.switch_mode_and_capture_file(
            cfg, self.image, signal_function=self.qpicamera2.signal_done
        )

    def capture_multiple_images(self):
        for i in range(self.number_of_images):
            self.on_button_clicked()
            time.sleep(3)
        self.number_of_images = 3

    def startDisplayImage(self, image=None):
        self.setWindowTitle("Image Title")
        self.display = DisplayImage(self)

        if image != None:
            self.display.openFile(image)
        self.menuBar.setVisible(True)
        self.fileMenu.addAction(self.display.openAction)
        self.fileMenu.addAction(self.display.exitAction)

        self.setCentralWidget(self.display)
        self.display.preview_button.clicked.connect(self.startPreviewWindow)

    def startPreviewWindow(self):
        self.setWindowTitle("Pi Camera Preview")
        # Create an instance fo the camera widget
        self.qpicamera2 = QGlPicamera2(
            self.picam2, width=1800, height=1200, keep_ar=False
        )
        self.qpicamera2.done_signal.connect(self.capture_done)

        self.window = PreviewCamera(self.qpicamera2, parent=self)
        # Start camera with preview configuration
        self.picam2.start()

        self.setCentralWidget(self.window)

        # Buttons linked to functions
        self.window.display_button.clicked.connect(self.startDisplayImage)
        self.window.capture_button.clicked.connect(self.on_button_clicked)
        self.window.capture_images_button.clicked.connect(self.showDialog)

    # On startup, use this for recurrent playback of the video
    def startVideoPlayback(self):
        self.isVideoPlayBack = True
        self.videoPlayback = VideoPlayback(self)
        self.setMouseTracking(True)
        self.setCentralWidget(self.videoPlayback)

    # Function for Video Player
    def startVideoWidget(self):
        self.setWindowTitle("PyQt Video Player Widget Example ")
        self.videoWidget = VideoWidget(self)

        self.menuBar.setVisible(True)
        self.fileMenu.addAction(self.videoWidget.openAction)
        self.fileMenu.addAction(self.videoWidget.exitAction)

        self.setCentralWidget(self.videoWidget)

    def startMainWindow(self):
        self.setWindowTitle("Main Menu")
        self.mainWindow = MainWindow(self)
        self.setCentralWidget(self.mainWindow)
        # Buttons linked to functions
        self.mainWindow.PreviewWindowbutton.clicked.connect(self.startPreviewWindow)
        # self.mainWindow.MediaPlayerbutton.clicked.connect(self.startVideoWidget)
        self.mainWindow.PhotoWindowbutton.clicked.connect(self.startDisplayImage)
        self.mainWindow.ExitWindowbutton.clicked.connect(self.exit)

    def startSignupForm(self):
        self.form = LoginForm(self)
        self.setCentralWidget(self.form)
        self.form.ExitWindowbutton.clicked.connect(self.startVideoPlayback)

    # Dialog box for inputting the number of photos taken
    def showDialog(self):
        self.inputDialog = NumImagePopUp()
        form_lbx = QVBoxLayout(self.inputDialog)

        self.inputDialog.setStyleSheet(style)

        self.le = QLineEdit()
        self.le.setValidator(QtGui.QIntValidator(1, 10))
        self.btn = QPushButton("Capture")
        self.btn.clicked.connect(self.acceptInput)

        form_lbx.addWidget(self.le)
        form_lbx.addWidget(self.btn)

        # self.inputDialog.setAutoFillBackground(True)
        self.inputDialog.setObjectName("NumImagePopUp")

        self.parent_center = self.mapToGlobal(self.rect().center())
        print(self.parent_center)

        # Position the widget relative to the parent
        self.inputDialog.move(
            int(self.parent_center.x() - self.inputDialog.width() / 2),
            int(self.parent_center.y() - self.inputDialog.height() / 2),
        )

        self.inputDialog.raise_()
        self.inputDialog.show()

    def acceptInput(self):
        try:
            self.number_of_images = int(self.le.text())
            self.exitInputDialog()
            self.capture_multiple_images()
        except:
            # Create a dialog box for messages
            print("Please enter integer between 1 and 10")
            pass

    def exitInputDialog(self):
        self.inputDialog.close()

    # Mouse event for moving mouse over video playback
    def mouseMoveEvent(self, event):
        # if current widget is VideoPlayback widget, stop playback, show default
        if event.type() == QEvent.MouseMove and self.isVideoPlayBack == True:
            self.startMainWindow()
            self.isVideoPlayBack = False

    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QtCore.QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)

        QWidget.setMouseTracking(self, flag)
        recursive_set(self)

    # def showDialog(self):
    #     dialog = LoginPopup(self)
    #     if dialog.exec_():
    #         print(dialog.email(), dialog.password())

    def exitCall(self):
        self.startVideoPlayback()
        self.menuBar.setVisible(False)

    def exit(self):
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = Window()
    sys.exit(app.exec_())
