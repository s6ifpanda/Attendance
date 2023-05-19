from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QFont, QShortcut, QKeySequence
from PyQt6.QtWidgets import QWidget, QTableWidget, QMenu, QTableWidgetItem, QVBoxLayout, QApplication, QDockWidget, \
    QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox

from database import Lecture, get_weeks, get_lectures

LECTURES = ("Lecture", "Duration", "Stage", "Assistance", "Week")
WEEKS = ('1', '2', '3', '4', '5', '6', '7', '8')
DEFAULT_ORDERING = ("lecture", "duration", "stage", "assistance")


class LecturesPage(QWidget):

    def __init__(self, data: List[Lecture], signal):
        super().__init__()
        self.signal = signal
        self.data = data
        self.lectures: dict[int, tuple[Lecture, CustomWidget]] = dict()
        self.dock_widget = QDockWidget()
        self.dock_widget.setFeatures(
            self.dock_widget.DockWidgetFeature.DockWidgetClosable | self.dock_widget.DockWidgetFeature.DockWidgetMovable)
        self.dock_widget.hide()
        self.table = LectureTables(len(data), len(LECTURES))
        self.initialize()

    def initialize(self):
        layout = QHBoxLayout()
        for index, lecture in enumerate(self.data):
            widget = CustomComboBox([str(week) for week in range(1, get_weeks(lecture.lecture_id)+1)])
            l = AbstractedLecture(lecture, self.table)
            l.add_lecture({widget})
            self.lectures[index] = (lecture, CustomWidget(lecture, combo_box=widget, signal=self.signal))

        self.table.itemSelectionChanged.connect(self.test)
        layout.addWidget(self.table, 2)
        layout.addWidget(self.dock_widget, 1)
        self.setLayout(layout)

    def test(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.table.clearFocus()
            self.dock_widget.hide()
            return
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        current_row = self.table.currentRow()
        self.dock_widget.setWidget(self.lectures[current_row][1])
        self.dock_widget.showNormal()


class CustomWidget(QWidget):
    def __init__(self, lecture_data: Lecture, combo_box=None, signal=None, week=None, button=True):
        super().__init__()
        self.combo_box = combo_box
        self.signal = signal
        self.lecture = lecture_data
        layout = QVBoxLayout()
        lecture = StyledLabel(lecture_data.name)
        stage = StyledLabel(f"Stage: {lecture_data.stage.removesuffix('Stage').strip()}", size=10, color="grey")
        duration = StyledLabel(f"Duration: {lecture_data.duration_simplified}", size=10, color="grey")
        ass = StyledLabel(f"Assistant: {lecture_data.assistant}", size=10, color="grey")
        if combo_box:
            box = StyledLabel(src=combo_box, is_src=1, size=10, color="grey")
        else:
            box = StyledLabel(f"Week: {week}", size=10, color="grey")
        layout.addWidget(lecture)
        layout.addWidget(stage)
        layout.addWidget(duration)
        layout.addWidget(ass)
        layout.addWidget(box)
        layout.addStretch(1)
        if button:
            button = QPushButton("Join", clicked=self.push_clicked)
            layout.addWidget(button)
            layout.addStretch(2)
        self.setLayout(layout)

    def push_clicked(self):
        current_text = self.combo_box.currentText()
        if current_text is not None and current_text.isdigit():
            self.signal.emit(self.lecture, int(current_text))
        else:
            QMessageBox.warning(self, "Warning!", "Please specify the week.")


class CustomTable(QTableWidget):
    def __init__(self, rows, columns, **kwargs):
        super().__init__(rows, columns)
        self.setStyleSheet(kwargs.get("stylesheet", ""))
        cut_shortcut = QShortcut(QKeySequence.StandardKey.Cut, self)
        cut_shortcut.activated.connect(self.copy_only)
        shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        shortcut.activated.connect(self.copy_text)
        self.setColumnWidth(0, int(self.width() / 4))
        # Applying Custom Options
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setWordWrap(False)
        self.setAcceptDrops(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(self.horizontalScrollBarPolicy().ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(self.verticalScrollBarPolicy().ScrollBarAlwaysOff)
        self.last_row = 0

    def add_row(self, iterable, widgets=None, start_index=0):
        for index, value in enumerate(iterable, start_index):
            self.setItem(self.last_row, index, QTableWidgetItem(str(value)))
        if widgets is not None:
            for widget in widgets:
                index += 1
                self.setCellWidget(self.last_row, index, widget)
        self.last_row += 1

    def contextMenuEvent(self, pos):
        if self.selectionModel().selection().indexes():
            row, column = self.currentRow(), self.currentColumn()
            menu = QMenu()
            item = self.item(row, column).text()
            menu.addAction("Copy Whole Row", "Ctrl+C", self.copy_text, Qt.ConnectionType.SingleShotConnection)
            menu.addAction(f"Copy {item} only", "Ctrl+X", self.copy_only, Qt.ConnectionType.SingleShotConnection)
            menu.exec(QCursor.pos())

    def copy_only(self):
        item = self.item(self.currentRow(), self.currentColumn()).text()
        QApplication.clipboard().setText(item, QApplication.clipboard().Mode.Clipboard)

    def copy_text(self):
        items = self.selectedItems()
        data = ""
        for item in items:
            if item.text().replace(".", "").isdigit():
                data += item.text().strip() + " Hours/"
                continue
            data += item.text() + "/"
        QApplication.clipboard().setText(data.removesuffix("/"), QApplication.clipboard().Mode.Clipboard)


class LectureTables(CustomTable):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.last_row = 0
        self.setHorizontalHeaderLabels(LECTURES)

    def add_lecture(self, lecture: Lecture, widgets=None):
        pass


class AbstractedLecture:
    default_ordering = ("Lecture", "Duration", "Stage", "Assistance")

    def __init__(self, lecture: Lecture, table: LectureTables):
        self.table = table
        self.lecture = lecture

    def add_lecture(self, widgets=None, ordering=DEFAULT_ORDERING):
        columns = []
        for column in ordering:
            match column:
                case "lecture":
                    columns.append(self.lecture.name)
                case "duration":
                    columns.append(self.lecture.duration_simplified)
                case "stage":
                    columns.append(self.lecture.stage)
                case "assistance":
                    columns.append(self.lecture.assistant)
        self.table.add_row(columns, widgets)


class StyledLabel(QLabel):
    def __init__(self, text="Not Specified", font_family="Lato", size=16, color=None, is_src=None, src=None):
        super().__init__(f"{text}")
        if is_src:
            self.t = src
            src.currentTextChanged.connect(self.change_text)
            self.change_text()
        self.setFont(QFont(font_family, size))
        if color:
            self.setStyleSheet(f"color: {color}")

    def change_text(self, new_text=None):
        if not new_text:
            new_text = "Not Specified"
        self.setText(f"Week: {new_text}")


class CustomComboBox(QComboBox):
    def __init__(self, items=None):
        super().__init__()
        self.setPlaceholderText("Specify Week")
        if items is not None:
            self.addItems(items)


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("Fusion")
    window = LecturesPage(get_lectures())
    window.show()
    app.exec()
