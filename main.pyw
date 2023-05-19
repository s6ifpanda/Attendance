import sys

from PyQt6.QtCore import QPropertyAnimation, QPoint, QEasingCurve, pyqtSignal, pyqtSlot, QParallelAnimationGroup, \
    QAbstractAnimation, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QGraphicsOpacityEffect

from AdmiralWindow import AdmiralWindow
from database import get_database, get_from_id, get_students, Lecture, get_users
from lectures import LecturesPage
from login import LoginPage
from recording import RecordingPage
from helpertools import hash_sha
with open("assets/light_mode.qss") as file:
    light_style = file.read()

with open("assets/dark_mode.qss") as file:
    dark_style = file.read()

del file


class MainWindow(QMainWindow):
    signal = pyqtSignal(str, str)
    button_signal = pyqtSignal(Lecture, int)
    back_signal = pyqtSignal(bool)

    def __init__(self, src: QApplication, parent=None):
        super().__init__(parent)
        self.data = None
        self.src = src
        self.__data_base = get_database()
        self.button_signal.connect(self.recording_navigate)
        self.login_page = LoginPage(self.signal)
        self.lectures = None
        self.signal.connect(self.sign_in)
        # users = get_users()
        self.setup_menu()
        self.back_signal.connect(self.back)
        # self.admiral = AdmiralWindow(get_users())
        self.src.setStyleSheet(light_style)
        self.setCentralWidget(self.login_page)
        # self.setCentralWidget(self.admiral)
        self.setMinimumSize(800, 500)
        self.showMaximized()
        self.show()
        self.start_animation()

    @pyqtSlot(bool)
    def back(self, value):
        self.lectures = LecturesPage(self.data, self.button_signal)
        self.setCentralWidget(self.lectures)
        self.lectures.hide()
        self.start_animation2(sign=1)

    @pyqtSlot(Lecture, int)
    def recording_navigate(self, lecture_info, week):
        students = get_students(lecture_info.stage_id)
        record = RecordingPage(students, lecture_info, week, self.back_signal)
        self.setCentralWidget(record)
        record.start_scanning()

    @pyqtSlot(str, str)
    def sign_in(self, username, password):
        for data in self.__data_base:
            if data.username == username:
                if data.password == hash_sha(password):
                    self.logout_action.setVisible(True)
                    match data.rank:
                        case data.rank.Teacher:
                            self.data = get_from_id(data.id)
                            self.lectures = LecturesPage(self.data, self.button_signal)
                            self.setCentralWidget(self.lectures)
                            self.lectures.hide()
                            self.start_animation2()
                            self.login_page.success_signal.emit(1)
                        case data.rank.Admin:
                            self.admiral = AdmiralWindow(data, get_users())
                            self.setCentralWidget(self.admiral)
                        case data.rank.Assistant:
                            self.admiral = AdmiralWindow(data, get_users())
                            self.setCentralWidget(self.admiral)

                self.login_page.success_signal.emit(0)
                return False
        self.login_page.success_signal.emit(0)
        return False


    def setup_menu(self):
        file_menu = self.menuBar().addMenu("File")
        # Dark Mode
        dark_mode = file_menu.addAction("&Dark_Mode")
        dark_mode.setCheckable(True)
        dark_mode.setShortcut("Ctrl+D")
        dark_mode.triggered.connect(self.dark_mode)
        self.logout_action = file_menu.addAction("&Sign Out")
        self.logout_action.triggered.connect(self.logout)
        self.logout_action.setVisible(False)
        # Exit
        exit_action = file_menu.addAction("&Quit")
        exit_action.triggered.connect(sys.exit)
        # About Menu
        about_menu = self.menuBar().addAction("&About")
        about_menu.triggered.connect(self.about)

    def logout(self):
        self.centralWidget().close()
        self.close()
        self.__init__(self.src)


    def dark_mode(self, activated: bool) -> None:
        self.src.setStyleSheet(dark_style) if activated else self.src.setStyleSheet(light_style)
        self.start_animation(500)

    def about(self) -> None:
        QMessageBox.information(self,
                                "About",
                                "Automated Attendance & Absence System For The College For The Department Of BIC")

    def start_animation(self, duration=1000):
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        opacity_animation = QPropertyAnimation(
            opacity_effect, b"opacity", duration=duration, startValue=0, endValue=1
        )
        group = QParallelAnimationGroup(self)
        group.addAnimation(opacity_animation)
        group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        QTimer().singleShot(duration, lambda: self.setGraphicsEffect(None))

    def start_animation2(self, sign=-1):
        self.animation = QPropertyAnimation(self.lectures, b'pos')
        self.animation.setDuration(500)
        geo = int(self.geometry().width())
        self.animation.setStartValue(QPoint((geo * sign), 30))
        self.animation.setEasingCurve(QEasingCurve.Type.BezierSpline)
        opacity_effect = QGraphicsOpacityEffect(self.lectures)
        opacity_effect.setOpacity(0)
        self.lectures.setGraphicsEffect(opacity_effect)
        opacity_animation = QPropertyAnimation(
            opacity_effect, b"opacity", duration=500, startValue=0, endValue=1
        )
        group = QParallelAnimationGroup(self)
        group.addAnimation(self.animation)
        group.addAnimation(opacity_animation)
        self.lectures.show()
        group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        QTimer().singleShot(500, lambda: self.lectures.setGraphicsEffect(None))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow(app)
    app.exec()
