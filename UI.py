# from PyQt5.QtGui import QApplication, QMainWindow, QPushButton, QWidget
# For PyQt5 :
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (
    QPushButton,
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QMessageBox,
    QHBoxLayout,
    QFileDialog,
    QHBoxLayout,
    QSizePolicy,
    QSlider,
    QLineEdit,
    QStyle,
    QAction,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtCore import QDir, Qt, QUrl, QEvent


class DisplayImage(QWidget):
    def __init__(self, parent=None):
        super(DisplayImage, self).__init__(parent)

        self.parent = parent
        # Create a label to identify this widget properly
        self.label = QLabel(self)

        self.image = QPixmap("/home/pi/photobooth/IMG_09_11_2023_13_28_23.jpg")
        self.label.setPixmap(self.image)
        # self.label.resize()

        # Create button to switch back to camera preview
        self.preview_button = QPushButton("preview button")

        # Create button for exiting to playback
        self.ExitWindowbutton = QPushButton("Exit")

        # Add Actions
        # Create new action
        self.openAction = QAction(QIcon("open.png"), "&Open", self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.setStatusTip("Open movie")
        self.openAction.triggered.connect(self.openFile)

        # Create exit action
        self.exitAction = QAction(QIcon("exit.png"), "&Exit", self)
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.setStatusTip("Exit Video Player")
        self.exitAction.triggered.connect(self.parent.exitCall)

        self.layout_v = QVBoxLayout(self)
        self.layout_h = QHBoxLayout()

        self.layout_h.addWidget(self.preview_button)

        self.layout_v.addWidget(self.label)
        self.layout_v.addLayout(self.layout_h)
        self.layout_v.addWidget(self.ExitWindowbutton)

        # self.setLayout(self.layout_v)

        self.ExitWindowbutton.clicked.connect(self.parent.startVideoPlayback)

    def openFile(self, fileName=None):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Photos", QDir.homePath())

        if fileName != "":
            self.image = QPixmap(fileName)
            self.label.setPixmap(self.image)


class PreviewCamera(QWidget):
    def __init__(self, picameraWidget, parent=None):
        super(PreviewCamera, self).__init__(parent)

        self.parent = parent
        # Button to switch to display
        self.display_button = QPushButton("Display Image")
        # Create button to use pi camera for capturing image
        self.capture_button = QPushButton("Capture Image")
        # Create button to use pi camera for capturing multiple images
        self.capture_images_button = QPushButton("Capture Multiple Images")
        # Create button for exiting to playback
        self.ExitWindowbutton = QPushButton("Exit")

        # Create layouts to hold picamera 2 feed and buttons
        self.layout_v = QVBoxLayout()
        self.layout_h = QHBoxLayout()

        self.layout_v.addWidget(picameraWidget)
        self.layout_h.addWidget(self.display_button)
        self.layout_h.addWidget(self.capture_button)
        self.layout_h.addWidget(self.capture_images_button)

        self.layout_v.addLayout(self.layout_h)
        self.layout_v.addWidget(self.ExitWindowbutton)

        self.setLayout(self.layout_v)

        self.ExitWindowbutton.clicked.connect(self.parent.startVideoPlayback)
        # self.capture_images_button.clicked.connect(self.parent.showDialog)
        # self.capture_images_button.clicked.connect(self.parent.showDialog)


class VideoWidget(QWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)

        self.parent = parent

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.ExitWindowbutton = QPushButton("Exit")

        self.video_widget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Create new action
        self.openAction = QAction(QIcon("open.png"), "&Open", self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.setStatusTip("Open movie")
        self.openAction.triggered.connect(self.openFile)

        # Create exit action
        self.exitAction = QAction(QIcon("exit.png"), "&Exit", self)
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.setStatusTip("Exit Video Player")
        self.exitAction.triggered.connect(self.parent.exitCall)

        # Create layouts to place inside widget
        self.controlLayout = QHBoxLayout()
        self.controlLayout.setContentsMargins(0, 0, 0, 0)
        self.controlLayout.addWidget(self.playButton)
        self.controlLayout.addWidget(self.positionSlider)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.video_widget)
        self.layout.addLayout(self.controlLayout)
        self.layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        # self.setLayout(self.layout)

        self.mediaPlayer.setVideoOutput(self.video_widget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())

        if fileName != "":
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())


class VideoPlayback(QWidget):
    def __init__(self, parent=None):
        super(VideoPlayback, self).__init__(parent)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        self.parent = parent

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.videoWidget)

        # self.setLayout(self.layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        file = "/home/tertese/Public/smat_projects/pyqt5_projects/photobooth/demo.mp4"

        self.playlist = QMediaPlaylist()

        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(file)))
        self.playlist.setCurrentIndex(1)
        self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        self.mediaPlayer.setPlaylist(self.playlist)

        self.mediaPlayer.play()

    def openFile(self, fileName):
        if fileName != "":
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))


class LoginForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login Form")
        self.resize(500, 120)

        layout = QGridLayout()

        self.ExitWindowbutton = QPushButton("Exit")

        label_name = QLabel('<font size=""> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText("Please enter your username")
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText("Please enter your password")
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        button_login = QPushButton("Login")
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 2, 0, 1, 2)
        layout.addWidget(self.ExitWindowbutton)
        layout.setRowMinimumHeight(2, 75)

        self.setLayout(layout)

    def check_password(self):
        msg = QMessageBox()

        if (
            self.lineEdit_username.text() == "Username"
            and self.lineEdit_password.text() == "000"
        ):
            msg.setText("Success")
            msg.exec_()
            app.quit()

        else:
            msg.setText("Incorrect Password")
            msg.exec_()


# Main Window
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.PreviewWindowbutton = QPushButton("Go To Preview Window")
        # self.MediaPlayerbutton = QPushButton("Go To Media Player")
        self.PhotoWindowbutton = QPushButton("Go To Photos")
        self.ExitWindowbutton = QPushButton("Exit")

        self.PreviewWindowbutton.setEnabled(True)
        # self.MediaPlayerbutton.setEnabled(True)
        self.PhotoWindowbutton.setEnabled(True)
        self.ExitWindowbutton.setEnabled(True)

        self.layout_v = QVBoxLayout(self)
        self.layout_v.addWidget(self.PreviewWindowbutton)
        # self.layout_v.addWidget(self.MediaPlayerbutton)
        self.layout_v.addWidget(self.PhotoWindowbutton)
        self.layout_v.addWidget(self.ExitWindowbutton)

        # self.setLayout(self.layout_v)
