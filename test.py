import sys
from typing import Dict

from PyQt6.QtGui import QFont, QColor, QGradient
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QListWidget, QPushButton

from database import Student


class RecordingPage(QWidget):
    def __init__(self, students: Dict[int, Student]):
        super().__init__()
        grid = QGridLayout()
        self.students = students
        self.setWindowTitle('QR Code Scanner')
        self.lst = QListWidget()
        self.lst.addItem("سجاج")
        self.lst2 = QListWidget()
        self.lst2.addItems((student.name for student in students.values()))
        self.colors = [i for i in QGradient.Preset if isinstance(i, QGradient.Preset)]
        # self.lst.addItem(account.name)
        self.scanned_student_ids = set()
        # Create a QLabel to display the video frame
        self.label = QLabel(self)
        self.index = 0
        self.btn = QPushButton("text", clicked=self.apply_style)
        grid.addWidget(self.btn, 0, 0)
        grid.addWidget(self.label, 1, 0)
        grid.addWidget(self.lst, 0, 1, 1, 1)
        grid.addWidget(self.lst2, 1, 1, 1, 1)
        self.setLayout(grid)
    def apply_style(self):
        palette = self.lst.palette()
        palette2 = self.lst2.palette()
        grad = QGradient(self.colors[self.index])
        self.label.setText(str(self.colors[self.index]))
        palette.setBrush(palette.ColorRole.Highlight, QGradient(QGradient.Preset.PhoenixStart))
        palette2.setColor(palette.ColorRole.Highlight, QColor('red'))
        self.lst.setPalette(palette)
        self.lst2.setPalette(palette2)
        self.lst2.setFont(QFont('Lato', 18))
        self.lst.setFont(QFont('Lato', 18))
        self.index += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    students = {1: Student(name='aya husham', email='ism_20_1@uoitc.edu.iq', id=1, qr_id=1, stage_id=4), 2: Student(name='aya mohammed', email='ism_20_2@uoitc.edu.iq', id=2, qr_id=2, stage_id=4), 3: Student(name='aseel kasim', email='ism_20_3@uoitc.edu.iq', id=3, qr_id=3, stage_id=4), 4: Student(name='abo alhassan ali', email='ism_20_4@uoitc.edu.iq', id=4, qr_id=4, stage_id=4), 5: Student(name='israa ahmed', email='ism_20_5@uoitc.edu.iq', id=5, qr_id=5, stage_id=4), 6: Student(name='asmaa salah', email='ism_20_6@uoitc.edu.iq', id=6, qr_id=6, stage_id=4), 7: Student(name='alaa muhsin]', email='ism_20_7@uoitc.edu.iq', id=7, qr_id=7, stage_id=4), 8: Student(name='ameer safaa', email='ism_20_8@uoitc.edu.iq', id=8, qr_id=8, stage_id=4), 9: Student(name='anfal muthana', email='ism_20_9@uoitc.edu.iq', id=9, qr_id=9, stage_id=4), 10: Student(name='tabarek sameer', email='ism_20_10@uoitc.edu.iq', id=10, qr_id=10, stage_id=4), 11: Student(name='tabarek mahdi', email='ism_20_11@uoitc.edu.iq', id=11, qr_id=11, stage_id=4), 12: Student(name='tayseer falah', email='ism_20_12@uoitc.edu.iq', id=12, qr_id=12, stage_id=4), 13: Student(name='janna rafa', email='ism_20_13@uoitc.edu.iq', id=13, qr_id=13, stage_id=4), 14: Student(name='hussein abbas', email='ism_20_14@uoitc.edu.iq', id=14, qr_id=14, stage_id=4), 15: Student(name='haneen kamran', email='ism_20_15@uoitc.edu.iq', id=15, qr_id=15, stage_id=4), 16: Student(name='danya ridha', email='ism_20_16@uoitc.edu.iq', id=16, qr_id=16, stage_id=4), 17: Student(name='dima omar', email='ism_20_17@uoitc.edu.iq', id=17, qr_id=17, stage_id=4), 18: Student(name='ranya ahmed', email='ism_20_18@uoitc.edu.iq', id=18, qr_id=18, stage_id=4), 19: Student(name='redha abbas', email='ism_20_19@uoitc.edu.iq', id=19, qr_id=19, stage_id=4), 20: Student(name='ruqaya raad', email='ism_20_20@uoitc.edu.iq', id=20, qr_id=20, stage_id=4), 21: Student(name='zainab thamir', email='ism_20_21@uoitc.edu.iq', id=21, qr_id=21, stage_id=4), 22: Student(name='zainab faris', email='ism_20_22@uoitc.edu.iq', id=22, qr_id=22, stage_id=4), 23: Student(name='saja munaf', email='ism_20_23@uoitc.edu.iq', id=23, qr_id=23, stage_id=4), 24: Student(name='saja akram', email='ism_20_24@uoitc.edu.iq', id=24, qr_id=24, stage_id=4), 25: Student(name='sura shihab', email='ism_20_25@uoitc.edu.iq', id=25, qr_id=25, stage_id=4), 26: Student(name='somaya ghani', email='ism_20_26@uoitc.edu.iq', id=26, qr_id=26, stage_id=4), 27: Student(name='shorooq naji', email='ism_20_27@uoitc.edu.iq', id=27, qr_id=27, stage_id=4), 28: Student(name='shahad abudl-hassan', email='ism_20_28@uoitc.edu.iq', id=28, qr_id=28, stage_id=4), 29: Student(name='shahzanan jassim', email='ism_20_29@uoitc.edu.iq', id=29, qr_id=29, stage_id=4), 30: Student(name='aalya abdul-kareem', email='ism_20_30@uoitc.edu.iq', id=30, qr_id=30, stage_id=4), 31: Student(name='ali amer', email='ism_20_31@uoitc.edu.iq', id=31, qr_id=31, stage_id=4), 32: Student(name='ghaith ahmed', email='ism_20_32@uoitc.edu.iq', id=32, qr_id=32, stage_id=4), 33: Student(name='fatima riyad', email='ism_20_33@uoitc.edu.iq', id=33, qr_id=33, stage_id=4), 34: Student(name='lina abdul-kareem', email='ism_20_34@uoitc.edu.iq', id=34, qr_id=34, stage_id=4), 35: Student(name='mohammed shihab', email='ism_20_35@uoitc.edu.iq', id=35, qr_id=35, stage_id=4), 36: Student(name='maryam ali', email='ism_20_36@uoitc.edu.iq', id=36, qr_id=36, stage_id=4), 37: Student(name='maryam ammar', email='ism_20_37@uoitc.edu.iq', id=37, qr_id=37, stage_id=4), 38: Student(name='maryam fouad', email='ism_20_38@uoitc.edu.iq', id=38, qr_id=38, stage_id=4), 39: Student(name='mustafa hassan', email='ism_20_39@uoitc.edu.iq', id=39, qr_id=39, stage_id=4), 40: Student(name='mustafa falah', email='ism_20_40@uoitc.edu.iq', id=40, qr_id=40, stage_id=4), 41: Student(name='muna mohammed', email='ism_20_41@uoitc.edu.iq', id=41, qr_id=41, stage_id=4), 42: Student(name='mahdi hajji', email='ism_20_42@uoitc.edu.iq', id=42, qr_id=42, stage_id=4), 43: Student(name='nabaa ali', email='ism_20_43@uoitc.edu.iq', id=43, qr_id=43, stage_id=4), 44: Student(name='nabaa eissa', email='ism_20_44@uoitc.edu.iq', id=44, qr_id=44, stage_id=4), 45: Student(name='nabaa maythem', email='ism_20_45@uoitc.edu.iq', id=45, qr_id=45, stage_id=4), 46: Student(name='nebras mahmoud', email='ism_20_46@uoitc.edu.iq', id=46, qr_id=46, stage_id=4), 47: Student(name='nabaa riyad', email='ism_20_47@uoitc.edu.iq', id=47, qr_id=47, stage_id=4), 48: Student(name='nora haitham', email='ism_20_48@uoitc.edu.iq', id=48, qr_id=48, stage_id=4), 49: Student(name='nawras khudair', email='ism_20_49@uoitc.edu.iq', id=49, qr_id=49, stage_id=4), 50: Student(name='hiba ahmed', email='ism_20_50@uoitc.edu.iq', id=50, qr_id=50, stage_id=4), 51: Student(name='hajas abdul-salam', email='ism_20_51@uoitc.edu.iq', id=51, qr_id=51, stage_id=4), 52: Student(name='haya moyad', email='ism_20_52@uoitc.edu.iq', id=52, qr_id=52, stage_id=4), 53: Student(name='weam jomaa', email='ism_20_53@uoitc.edu.iq', id=53, qr_id=53, stage_id=4), 54: Student(name='yousif layth', email='ism_20_54@uoitc.edu.iq', id=54, qr_id=54, stage_id=4), 55: Student(name='ahmed mohammed', email='ism_20_55@uoitc.edu.iq', id=55, qr_id=55, stage_id=4), 56: Student(name='rand khalil', email='ism_20_56@uoitc.edu.iq', id=56, qr_id=56, stage_id=4), 57: Student(name='sajad ali', email='ism_20_57@uoitc.edu.iq', id=57, qr_id=57, stage_id=4), 58: Student(name='saif al-islam khalil', email='ism_20_58@uoitc.edu.iq', id=58, qr_id=58, stage_id=4), 59: Student(name='taha abdul-sattar', email='ism_20_59@uoitc.edu.iq', id=59, qr_id=59, stage_id=4), 60: Student(name='abbas kareem', email='ism_20_60@uoitc.edu.iq', id=60, qr_id=60, stage_id=4), 61: Student(name='abdullah mahdi', email='ism_20_61@uoitc.edu.iq', id=61, qr_id=61, stage_id=4), 62: Student(name='ali abdul-hadi', email='ism_20_62@uoitc.edu.iq', id=62, qr_id=62, stage_id=4), 63: Student(name='murtaza imad', email='ism_20_63@uoitc.edu.iq', id=63, qr_id=63, stage_id=4), 64: Student(name='husham mohammed', email='ism_20_64@uoitc.edu.iq', id=64, qr_id=64, stage_id=4)}
    with open("assets/light_mode.qss") as file:
        light_style = file.read()
    window = RecordingPage(students)
    window.show()
    # window.start_scanning()
    sys.exit(app.exec())
