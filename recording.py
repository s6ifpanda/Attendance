import sqlite3
from datetime import datetime
from typing import Dict
import cv2
from PyQt6.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QAbstractAnimation, QTimer
from PyQt6.QtGui import QImage, QPixmap, QFont, QGradient
from PyQt6.QtWidgets import QLabel, QWidget, QGridLayout, QListWidget, QPushButton, \
    QHBoxLayout, QGraphicsOpacityEffect
from playsound import playsound
from pyzbar.pyzbar import decode
from database import Student, Lecture
from lectures import CustomWidget

Connection = sqlite3.connect('attendance.db')
Cursor = Connection.cursor()


class RecordingPage(QWidget):
    def __init__(self, students: Dict[int, Student], lecture_info: Lecture, week, signal):
        super().__init__()
        grid = QGridLayout()
        self.lecture_id = lecture_info.lecture_id
        self.students = students
        self.week = week
        self.students_copy = students.copy()
        self.signal = signal
        self.info = CustomWidget(lecture_info, week=str(week), button=False)
        self.scanned_text = "{name} Scanned Successfully"
        self.already_scanned_text = "{name} Already Scanned"
        self.scanned = QLabel()
        self.already_scanned = QLabel()
        self.not_valid = QLabel("Not Valid QR Code")
        self.scanned.hide()
        self.already_scanned.hide()
        self.not_valid.hide()
        self.setWindowTitle('QR Code Scanner')
        self.lst = QListWidget()
        self.lst2 = QListWidget()
        self.lst2.addItems((student.name for student in students.values()))
        self.apply_style()
        self.scanned_student_ids = set()
        # Create a QLabel to display the video frame
        self.apply = QPushButton("Apply", clicked=self.apply_clicked)
        self.cancel = QPushButton("Cancel")
        self.back = QPushButton("Back to previous window", clicked=self.previous_clicked)
        self.label = QLabel(self)
        box = QHBoxLayout()
        box.addWidget(self.back)
        box.addWidget(self.apply)
        grid.addWidget(self.label, 0, 1)
        grid.addWidget(self.lst, 0, 0, 1, 1)
        grid.addWidget(self.lst2, 1, 0, 1, 1)
        grid.addWidget(self.scanned, 1, 1, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(self.already_scanned, 1, 1, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(self.not_valid, 1, 1, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(self.info, 1, 1, Qt.AlignmentFlag.AlignTop)
        grid.addLayout(box, 2, 1, alignment=Qt.AlignmentFlag.AlignBottom)
        self.setLayout(grid)
        for i in range(5):
            try:
                self.capture = cv2.VideoCapture(i)
                break
            except:
                continue
        self.capture.set(3, 360)
        self.capture.set(4, 480)

    def start_scanning(self):
        self.timer = self.startTimer(5)

    def apply_clicked(self):
        for account in self.students_copy.values():
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Cursor.execute(f'''INSERT INTO Attendance (Student_id, Student_name, Student_email, Student_qr_code_id, Stage_id, Stage_description, Lecture_id, Lecture_name, Lecture_week, State, Record_Date)
                                          VALUES ({account.id},
                                                  (SELECT Student_name FROM Students WHERE Student_id = {account.id}),
                                                  (SELECT Student_email FROM Students WHERE Student_id = {account.id}),
                                                  (SELECT Student_qr_code_id FROM Students WHERE Student_id = {account.id}),
                                                  {account.stage_id},
                                                  (SELECT Stage_description FROM Stages WHERE Stage_id = {account.stage_id}),
                                                  {self.lecture_id},
                                                  (SELECT Lecture_name FROM Lectures WHERE Lecture_id = {self.lecture_id}),
                                                  {self.week},
                                                  'Absent',
                                                  '{time_now}')''')
        self.students_copy.clear()
        Connection.commit()

    def previous_clicked(self):
        self.signal.emit(True)

    def apply_style(self):
        palette = self.lst.palette()
        palette2 = self.lst2.palette()
        palette.setBrush(palette.ColorRole.Highlight, QGradient(QGradient.Preset.GrownEarly))
        palette2.setBrush(palette.ColorRole.Highlight, QGradient(QGradient.Preset.StrongBliss))
        self.lst.setPalette(palette)
        self.lst2.setPalette(palette2)
        self.scanned.setStyleSheet(
            "color: qlineargradient(x1: 0, y1: 1, x2: 0, y2: 0, stop: 0 #37ecba, stop: 1 #72afd3);")
        self.already_scanned.setStyleSheet(
            "color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #f6d365, stop: 1 #fda085);")
        self.not_valid.setStyleSheet(
            "color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #f43b47, stop: 0.5 #453a94, stop: 1 #f43b47);")
        self.scanned.setFont(QFont("Arial", 18))
        self.already_scanned.setFont(QFont("Arial", 18))
        self.not_valid.setFont(QFont("Arial", 18))
        self.lst2.setFont(QFont('Lato', 15))
        self.lst.setFont(QFont('Arial', 15))

    def timerEvent(self, event):
        success, frame = self.capture.read()
        for i in decode(frame):
            id_decoded = int(i.data.decode('utf-8'))
            account = self.students.get(id_decoded)
            if account is None:
                print('Value Mis-Matched')
                self.scanned.hide()
                self.already_scanned.hide()
                self.not_valid.show()
                continue
            if id_decoded not in self.scanned_student_ids:
                self.scanned_student_ids.add(id_decoded)
                item = self.lst2.findItems(account.name, Qt.MatchFlag.MatchFixedString)[0]
                self.lst2.takeItem(self.lst2.row(item))
                self.lst.addItem(account.name)
                time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                Cursor.execute(f'''INSERT INTO Attendance (Student_id, Student_name, Student_email, Student_qr_code_id, Stage_id, Stage_description, Lecture_id, Lecture_name, Lecture_week, State, Record_Date)
                                  VALUES ({account.id},
                                          (SELECT Student_name FROM Students WHERE Student_id = {account.id}),
                                          (SELECT Student_email FROM Students WHERE Student_id = {account.id}),
                                          (SELECT Student_qr_code_id FROM Students WHERE Student_id = {account.id}),
                                          {account.stage_id},
                                          (SELECT Stage_description FROM Stages WHERE Stage_id = {account.stage_id}),
                                          {self.lecture_id},
                                          (SELECT Lecture_name FROM Lectures WHERE Lecture_id = {self.lecture_id}),
                                          {self.week},
                                          'Attendant',
                                          '{time_now}')''')
                playsound('assets/beep.mp3')
                self.already_scanned.hide()
                self.not_valid.hide()
                self.scanned.setText(self.scanned_text.format(name=account.name))
                self.scanned.show()
                try:
                    self.students_copy.pop(id_decoded)
                except KeyError:
                    pass
            else:
                print("Value Already Scanned")
                self.scanned.hide()
                self.not_valid.hide()
                self.already_scanned.setText(self.already_scanned_text.format(name=account.name))
                self.already_scanned.show()
                playsound('assets/already_scanned.mp3')
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        qimage = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.label.setPixmap(pixmap)

    def start_animation(self, widget: QLabel, duration=5000):
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        opacity_animation = QPropertyAnimation(
            opacity_effect, b"opacity", duration=duration, startValue=0.5, endValue=1
        )
        group = QParallelAnimationGroup(widget)
        group.addAnimation(opacity_animation)
        group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        QTimer().singleShot(duration, lambda: widget.setHidden(True))



