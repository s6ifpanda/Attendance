from datetime import datetime
from typing import Callable, Mapping

import pandas as pd
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QFont, QCursor, QAction, QPixmap, QColor, QBrush
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QPushButton, QWidget, QMenu, \
    QApplication, QFormLayout, QCalendarWidget, QMessageBox, QComboBox, QCheckBox, QHeaderView, \
    QFileDialog, QDialog, QWidgetAction, QTableWidget, QTableWidgetItem, QSpinBox, QTabWidget, QGroupBox, QSizePolicy, \
    QStackedLayout

from database import Account, add_new, get_users, delete_from_id, get_students, new_student, delete_student, get_stages, \
    get_teacher_id, delete_user, get_theories_lectures, reset_password, get_students_emails, get_attendances, \
    get_teachers_emails, make_admin_report, get_teachers_by_stage, delete_attendances
from database import get_teachers_names, get_teacher_name, get_lectures_info, insert_data, delete_lecture
from helpertools import elegant_time, unelegant_time, hash_sha, sending_email, student_report
from lectures import CustomTable
from login import PasswordEdit

HEADERS = ("ID", "Name", "Email", "Username", "Password", "Rank", "Birthday", "Action")
STUDENT_HEADERS = ('', "Name", "Email", "Stage", "QR_ID")
AUTHORITIES = ("Admiral", "Co-Admiral", "Teacher")


def excel_import(file):
    reader = pd.read_excel(file)
    return reader.to_records(False)


def excel_export(data):
    reader = pd.DataFrame(data)
    dialog = QFileDialog()
    dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    dialog.setDefaultSuffix("xlsx")
    file, _ = dialog.getSaveFileName(dialog, "Save File", "", "Excel files (*.xlsx)")
    if file:
        reader.to_excel(file, index=False)


class AdmiralWindow(QWidget):
    def __init__(self, user, users: list[Account]):
        super().__init__()
        self.users = users
        self.user = user
        self.main_layout = QHBoxLayout()
        self.dock_layout = QVBoxLayout()
        home_window = HomeWindow(user.name)
        self.current_widget = home_window
        self.init_ui()
        self.main_layout.addLayout(self.dock_layout)
        self.main_layout.addWidget(self.current_widget, 1)
        self.setLayout(self.main_layout)
        self.setWindowTitle("Admiral Dashboard")

    def init_ui(self):
        # Home
        home_dashboard = DashButton("Home", clicked=self.home_clicked)
        self.dock_layout.addWidget(home_dashboard)
        # Teachers
        teachers_dashboard = DashButton("Instructors", clicked=self.teachers_clicked)
        self.dock_layout.addWidget(teachers_dashboard)

        # Students
        students_dashboard = DashButton("Students", clicked=self.students_clicked)
        self.dock_layout.addWidget(students_dashboard)

        # Lectures Window
        lectures_dashboard = DashButton("Lectures", clicked=self.lectures_clicked)
        self.dock_layout.addWidget(lectures_dashboard)

        reporting_dashboard = DashButton("Reporting", clicked=self.reporting_clicked)
        self.dock_layout.addWidget(reporting_dashboard)

        self.dock_layout.addStretch(1)
    def home_clicked(self):
        self.current_widget.setHidden(True)
        self.current_widget.destroy(True, True)
        home_window = HomeWindow(self.user.name)
        self.main_layout.removeWidget(self.current_widget)
        self.current_widget = home_window
        self.main_layout.addWidget(self.current_widget, 1)

    def teachers_clicked(self):
        self.current_widget.setHidden(True)
        self.current_widget.destroy(True, True)
        teachers_window = TeachersWindow(self.user)
        teachers_window.signal.connect(self.teachers_clicked)
        self.main_layout.removeWidget(self.current_widget)
        self.current_widget = teachers_window
        self.main_layout.addWidget(self.current_widget, 1)

    def students_clicked(self):
        self.current_widget.setHidden(True)
        self.current_widget.destroy(True, True)
        students_window = StudentsWindow()
        students_window.signal.connect(self.students_clicked)
        self.main_layout.removeWidget(self.current_widget)
        self.current_widget = students_window
        self.main_layout.addWidget(self.current_widget, 1)

    def lectures_clicked(self):
        self.current_widget.setHidden(True)
        self.current_widget.destroy(True, True)
        lectures_window = LecturesWindow()
        lectures_window.signal.connect(self.lectures_clicked)
        self.main_layout.removeWidget(self.current_widget)
        self.current_widget = lectures_window
        self.main_layout.addWidget(self.current_widget, 1)

    def reporting_clicked(self):
        self.current_widget.setHidden(True)
        self.current_widget.destroy(True, True)
        reporting_window = ReportWindow()
        reporting_window.signal.connect(self.reporting_clicked)
        self.main_layout.removeWidget(self.current_widget)
        self.current_widget = reporting_window
        self.main_layout.addWidget(self.current_widget, 1)


class HomeWindow(QWidget):
    def __init__(self, name):
        super().__init__()
        vbox = QVBoxLayout()
        welcome_label = QLabel(f"Welcome Back, {name}")
        welcome_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        vbox.addWidget(welcome_label, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        vbox.addSpacing(50)
        self.setLayout(vbox)


class DashButton(QPushButton):
    def __init__(self, text="", **kwargs):
        super().__init__(text, **kwargs)
        self.setStyleSheet("""
        QPushButton {
            padding: 40px 40px 40px 40px;
            background-color: #3498db;
            font-weight: bold;
            margin: 0;
            color: white;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        """)


class TeachersWindow(QWidget):
    signal = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.users = get_users()
        self.table = CustomTeacher(len(self.users), 8)
        self.hor_box = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.new_window = NewTeacher(0, self.signal)
        self.setWindowTitle("Instructors")
        self.init_ui()
        self.setLayout(self.vbox)

    def init_ui(self):
        # First
        title = QLabel("Instructors")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        new_teacher = QPushButton("New Instructor", clicked=self.new_clicked)
        new_teacher.setStyleSheet("""
        QPushButton {
            background-color: #2ecc71;
            font-weight: bold;
            color: white;
            border-radius: 5px;
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: #27ae60;
        }
        """)
        self.hor_box.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)
        self.hor_box.addWidget(new_teacher, alignment=Qt.AlignmentFlag.AlignRight)
        self.vbox.addLayout(self.hor_box)
        self.vbox.addSpacing(10)

        # Second
        self.init_table()

    def init_table(self):
        self.users = get_users()
        self.table = CustomTeacher(len(self.users), 8)
        self.table.setHorizontalHeaderLabels(HEADERS)
        for account in self.users:
            reset_button = ResetButton(account.id, account.name, self.signal, "Reset Password")
            if account != self.user:
                delete_btn = DeleteButton(account.id, account.name, self.signal, "Delete")
            else:
                delete_btn = QLabel("Ops, you can't delete yourself!")
                delete_btn.setFont(QFont("Arial", 12))
            self.table.add_row((account.id,
                                account.name,
                                account.email,
                                account.username,
                                account.password,
                                account.rank,
                                account.birthday,
                                ), widgets=(CoupleButtons(delete_btn, reset_button),))
        self.vbox.addWidget(self.table)

    def new_clicked(self):
        self.new_window = NewTeacher(0, self.signal)
        self.new_window.showMaximized()

    def delete_table(self, id):
        ...  # COLORS UPDATED TOO I know, but I have to do both I mean from UI yup this is ez


class CustomTeacher(CustomTable):
    def __init__(self, row, column):
        super().__init__(row, column)
        self.setSelectionBehavior(self.SelectionBehavior.SelectItems)
        self.horizontalHeader().setStretchLastSection(True)

    def contextMenuEvent(self, pos):
        if self.selectionModel().selection().indexes():
            row, column = self.currentRow(), self.currentColumn()
            menu = QMenu()
            item = self.item(row, column)
            if item is None:
                return
            item = item.text()
            menu.addAction("Copy Whole Row", "Ctrl+C", self.copy_text, Qt.ConnectionType.SingleShotConnection)
            menu.addAction(f"Copy {item} only", "Ctrl+X", self.copy_only, Qt.ConnectionType.SingleShotConnection)
            menu.addAction("Delete")
            menu.exec(QCursor.pos())

    def copy_text(self):
        row_index = self.currentRow()
        num_cols = self.columnCount()

        items = []

        for i in range(num_cols):
            item = self.item(row_index, i)
            text = item.text() if item is not None else ""
            items.append(text)

        data = ""
        for item in items:
            data += item + "/"
        QApplication.clipboard().setText(data.removesuffix("/"), QApplication.clipboard().Mode.Clipboard)


class SpecialButton(QPushButton):
    def __init__(self, text, bg=None, **kwargs):
        super().__init__(text, **kwargs)
        if bg:
            self.setStyleSheet(f"background: {bg};")
        self.setMaximumWidth(75)


class NewTeacher(QWidget):

    def __init__(self, adder_id, signal):
        super().__init__()
        # Layouts
        self.signal = signal
        self.main_layout = QVBoxLayout()
        self.buttons_box = QHBoxLayout()
        self.layout = QFormLayout()
        self.layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # Window Info
        self.title = QLabel("New Instructor")
        self.title.setFont(QFont("Arial", 24))
        self.setWindowTitle("New Instructor")
        self.setContentsMargins(20, 5, 0, 10)

        # Applying layouts
        self.init_ui()
        self.main_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addLayout(self.layout, 1)
        self.main_layout.addLayout(self.buttons_box)
        self.setLayout(self.main_layout)

    def init_ui(self):
        # Name
        name_entry = QLineEdit()
        self.layout.addRow("Name", name_entry)

        # Email
        email_entry = QLineEdit()
        self.layout.addRow("Email", email_entry)

        # Username
        username_entry = QLineEdit()
        self.layout.addRow("Username", username_entry)

        # Password
        password_entry = PasswordEdit()
        self.layout.addRow("Password", password_entry)

        # Authority
        authority_box = QComboBox()
        authority_box.addItems(AUTHORITIES)
        self.layout.addRow("Authority", authority_box)

        # Birthdate
        birthdate_box = QCalendarWidget()

        self.layout.addRow("Birthdate MM/DD/YYYY", birthdate_box)

        # Submit
        self.buttons_box.addStretch()
        submit = SpecialButton("Submit", "green", clicked=lambda: self.submit_clicked(
            name_entry.text(),
            email_entry.text(),
            username_entry.text(),
            hash_sha(password_entry.text()),
            authority_box.currentText(),
            birthdate_box))
        self.buttons_box.addWidget(submit, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Cancel
        cancel = SpecialButton("Cancel", "red", clicked=self.close)
        self.buttons_box.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.buttons_box.addStretch()

    def submit_clicked(self, name, email, username, password, authority, birthdate):
        birth = birthdate.selectedDate().toString("yyyy-MM-dd")
        if not name or not email or not username or not password:
            return

        rank = None
        match authority:
            case "Admiral":
                rank = 1
            case "Co-Admiral":
                rank = 2
            case "Teacher":
                rank = 3
        add_new(name, email, username, password, birth, authority, rank)
        self.close()

    def closeEvent(self, a0) -> None:
        self.signal.emit()
        super().closeEvent(a0)


class ResetButton(SpecialButton):
    def __init__(self, user_id, user_name, signal, text="", **kwargs):
        super().__init__(text, "#FFA500", **kwargs)
        self.signal = signal
        self.user_id = user_id
        self.user_name = user_name
        self.clicked.connect(self.reset)

    def reset(self):
        self.w = NewPassword(self.user_id, self.user_name)
        self.w.show()


class DeleteButton(SpecialButton):
    def __init__(self, user_id, user_name, signal, text="", **kwargs):
        super().__init__(text, "#DC143C", **kwargs)
        self.signal = signal
        self.user_id = user_id
        self.user_name = user_name
        self.clicked.connect(self.delete)

    def delete(self):
        self.setStyleSheet("")
        self.widget = QMessageBox.question(self, "Prompt", f"Deleting This Instructor Will Delete All Of His / Her Associated Lectures, Are you sure you want to delete {self.user_name}?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)
        if self.widget == QMessageBox.StandardButton.Yes:
            delete_user(self.user_id)
        self.signal.emit()


class Question(QMessageBox):
    def __init__(self, obj, title, text, buttons, default_button):
        super().__init__()
        self.question(self, title, text, buttons, default_button)


class StudentsWindow(QWidget):
    signal = pyqtSignal()
    select_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.check_boxes = []
        self.setWindowTitle("Students")
        self.main_layout = QGridLayout()
        final_length = 0
        for i in FilterButton.options:
            final_length += len(get_students(i))
        self.table = CustomTeacher(final_length, 5)
        self.init_ui()
        self.setLayout(self.main_layout)
        self.select_signal.connect(self.select_all)
        self.select_all(False)

    def init_ui(self):
        # Title
        label_title = QLabel("Students", font=QFont("Arial", 24, QFont.Weight.DemiBold))
        self.main_layout.addWidget(label_title, 0, 0, 1, 3,
                                   alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        # import & export
        buttons_layout = QHBoxLayout()
        self.student = NewStudent()
        self.student.ok_btn.clicked.connect(self.new_student_clicked)
        import_button = DropButton("Import", {'From Excel': self.import_excel_info,
                                              'Manual Add': self.student.show})
        import_button.setToolTip("Import new data to the table")
        export_button = QPushButton("Export", clicked=self.export_table)
        export_button.setToolTip("Export filtered data as xlsx")
        buttons_layout.addWidget(import_button)
        buttons_layout.addWidget(export_button)
        buttons_layout.addStretch()
        self.main_layout.addLayout(buttons_layout, 2, 0)

        # Filter
        filter_button = FilterButton(self.signal)
        filter_button.setMaximumHeight(60)
        self.main_layout.addWidget(filter_button, 2, 2, alignment=Qt.AlignmentFlag.AlignBaseline)

        # Table
        # table.setHorizontalHeaderLabels(STUDENT_HEADERS)
        # table.setHorizontalHeaderItem(0, item)
        check_box = CheckBoxHeader(self.table, self.select_signal)
        self.table.setHorizontalHeader(check_box)
        self.table.setHorizontalHeaderLabels(STUDENT_HEADERS)
        self.table.horizontalHeader().setStretchLastSection(True)
        row = 0
        for i in FilterButton.options:
            for student in get_students(i).values():
                button = CustomCheckBox(self.table, row, student.id, check_box.checkbox)
                self.table.add_row([student.name, student.email, student.stage_id, student.qr_id], start_index=1)
                self.table.setCellWidget(row, 0, QCheckBox())
                self.check_boxes.append(button)
                row += 1

        # table.setCellWidget(0, 0, check)
        self.main_layout.addWidget(self.table, 3, 0, 3, 3)

        # Remove
        remove = SpecialButton("Delete All", "red", clicked=self.delete_selected)
        self.main_layout.addWidget(remove, 7, 2)

    def new_student_clicked(self):
        for row in range(self.student.table.rowCount()):
            new_student(self.student.table.item(row, 0).text(), self.student.table.item(row, 1).text(),
                        int(self.student.table.item(row, 2).text()), int(self.student.table.item(row, 3).text()))
        self.signal.emit()
        self.student.close()

    def export_table(self):
        data = {"Name": [], "Email": [], "Stage": [], "QR_ID": []}
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 1)
            email = self.table.item(row, 2)
            stage = self.table.item(row, 3)
            qr_id = self.table.item(row, 4)
            data['Name'].append(name.text() if name else None)
            data['Email'].append(email.text() if email else None)
            data['Stage'].append(
                int(stage.text()) if stage and stage.text().isdigit() else stage.text() if stage else None)
            data['QR_ID'].append(
                int(qr_id.text()) if qr_id and qr_id.text().isdigit() else qr_id.text() if qr_id else None)
        excel_export(data)

    def select_all(self, gate):
        for c in self.check_boxes:
            c.setChecked(gate)
            c.check_clicked(gate)
            self.table.setCellWidget(c.row, 0, c)

    def delete_selected(self):
        reply = QMessageBox.warning(
            self,
            "Title",
            "This Will Delete All Of The Selected Students, Are You Sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for check_box in self.check_boxes:
                if check_box.isChecked():
                    delete_student(check_box.unique_id)
            self.signal.emit()

    def import_excel_info(self):
        file, ok = QFileDialog.getOpenFileName(self, caption="Excel file",
                                               filter="Excel Files (*.xlsx *.xls *.xlsm *.xlsb);;CSV Files (*.csv)")
        if ok:
            data = excel_import(file)
            for row in data:
                s, t = row[2], row[3]
                new_student(row[0], row[1], int(s) if s else None, int(t) if t else None)
        self.signal.emit()


class DropButton(SpecialButton):
    def __init__(self, text, options: Mapping[str, Callable], **kwargs):
        super().__init__(text, **kwargs)
        # Create the dropdown menu and actions
        self.dropdown_menu = QMenu(self)
        for k, v in options.items():
            option = QAction(k, self)
            option.triggered.connect(v)
            self.dropdown_menu.addAction(option)

        # Set the menu to the button
        self.setMenu(self.dropdown_menu)


class CheckBoxHeader(QHeaderView):
    def __init__(self, parent, signal):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.checkbox = QCheckBox(self)
        self.checkbox.setChecked(False)
        self.checkbox.clicked.connect(lambda checked: signal.emit(checked))
        self.sectionResized.connect(self.adjustCheckbox)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        if logicalIndex == 0:
            checkbox_rect = self.checkbox.geometry()
            checkbox_rect.moveCenter(rect.center())
            pixmap = QPixmap(checkbox_rect.size())
            self.checkbox.render(pixmap)
            painter.drawPixmap(checkbox_rect.topRight(), pixmap)
        painter.restore()

    def adjustCheckbox(self, logicalIndex, oldSize, newSize):
        if logicalIndex == 0:
            checkbox_rect = self.checkbox.geometry()
            checkbox_rect.moveCenter(QRectF(0, 0, oldSize, self.height()).right())
            self.checkbox.setGeometry(checkbox_rect)


class FilterButton(QDialog):
    options = [1, 2, 3, 4]

    def __init__(self, signal):
        super().__init__()
        # Create the push button
        self.filter_button = QPushButton('Filter', self)
        # Create the dropdown menu with checkboxes
        self.dropdown_menu = QMenu(self)
        # Create checkboxes
        self.checkboxes = []
        for i in range(1, 5):
            checkbox = QCheckBox(f"Stage {i}")
            if i in self.options:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
            self.checkboxes.append(checkbox)
            action = QWidgetAction(self.dropdown_menu)
            action.setDefaultWidget(checkbox)
            self.dropdown_menu.addAction(action)

        # Create the apply button and add it to the layout
        self.apply_button = QPushButton('Apply', self, clicked=signal.emit)

        # Add checkboxes and Apply button to a horizontal layout
        box = QVBoxLayout()
        for checkbox in self.checkboxes:
            box.addWidget(checkbox)
        # box.addStretch()
        self.dropdown_menu.setLayout(box)
        box.addWidget(self.apply_button)

        # Set up the layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.filter_button)
        vbox.setSpacing(0)  # Set spacing to 0
        vbox.addWidget(self.dropdown_menu)
        vbox.addStretch()  # Add stretch to push Apply button to the bottom
        self.setLayout(vbox)
        self.checkboxes[0].clicked.connect(self.first_clicked)
        self.checkboxes[1].clicked.connect(self.second_clicked)
        self.checkboxes[2].clicked.connect(self.third_clicked)
        self.checkboxes[3].clicked.connect(self.fourth_clicked)
        # Connect the button to the dropdown menu
        self.filter_button.clicked.connect(self.show_dropdown)
        self.dropdown_menu.setMinimumSize(130, 150)

    def first_clicked(self, checked):
        if 1 in self.options:
            self.options.remove(1)
        if checked:
            self.options.append(1)

    def second_clicked(self, checked):
        if 2 in self.options:
            self.options.remove(2)
        if checked:
            self.options.append(2)

    def third_clicked(self, checked):
        if 3 in self.options:
            self.options.remove(3)
        if checked:
            self.options.append(3)

    def fourth_clicked(self, checked):
        if 4 in self.options:
            self.options.remove(4)
        if checked:
            self.options.append(4)

    def show_dropdown(self):
        # Show the dropdown menu
        self.dropdown_menu.popup(self.filter_button.mapToGlobal(self.filter_button.rect().bottomLeft()))

        # Connect the apply button to the hide_dropdown method
        self.apply_button.clicked.connect(self.hide_dropdown)

    def hide_dropdown(self):
        # Hide the dropdown menu and disconnect the apply button
        self.dropdown_menu.hide()
        self.apply_button.clicked.disconnect(self.hide_dropdown)


class CustomCheckBox(QCheckBox):
    def __init__(self, table, row, unique_id, main_checkbox: QCheckBox):
        super().__init__()
        self.row = row
        self.unique_id = unique_id
        self.main_checkbox = main_checkbox
        self.table = table
        self.clicked.connect(self.check_clicked)

    def check_clicked(self, checked):
        if not checked:
            self.main_checkbox.setChecked(False)
        bg = "#0077be" if checked else ""
        fg = "white" if checked else ""
        for i in range(1, self.table.columnCount()):
            item = self.table.item(self.row, i)
            if item is not None:
                item.setBackground(QColor(bg) if bg else QBrush())
                item.setForeground(QColor(fg) if fg else QBrush())


class CustomDeleteButton(SpecialButton):
    def __init__(self, text, bg, row, **kwargs):
        super().__init__(text, bg, **kwargs)
        self.row = row


class NewStudent(QWidget):
    rows: list[CustomDeleteButton] = []

    def __init__(self):
        super().__init__()

        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Email", "Stage", "QR Code", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout = QVBoxLayout()
        form = QFormLayout()
        self.name = QLineEdit()
        self.email = QLineEdit()
        self.stages = QComboBox()
        self.stages.addItems(get_stages())
        self.qr_code = QSpinBox()
        self.qr_code.setRange(0, 1000)
        form.addRow("Name:", self.name)
        form.addRow("Email:", self.email)
        form.addRow("Stage:", self.stages)
        form.addRow("QR Code:", self.qr_code)
        buttons = QHBoxLayout()
        append_btn = QPushButton("Append")
        append_btn.clicked.connect(self.append_row)
        cancel_btn = QPushButton("Cancel", clicked=self.close)
        self.ok_btn = QPushButton("OK")
        buttons.addWidget(cancel_btn)
        buttons.addWidget(self.ok_btn)
        layout.addLayout(form)
        layout.addWidget(append_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.table)
        layout.addLayout(buttons)
        self.setLayout(layout)
        self.setWindowTitle("Adding new student")

    def append_row(self):
        row = self.table.rowCount()
        self.table.setRowCount(row + 1)
        self.table.setItem(row, 0, QTableWidgetItem(self.name.text()))
        self.table.setItem(row, 1, QTableWidgetItem(self.email.text()))
        self.table.setItem(row, 2, QTableWidgetItem(str(self.stages.currentIndex() + 1)))
        self.table.setItem(row, 3, QTableWidgetItem(self.qr_code.text()))
        remove = CustomDeleteButton("Delete", "red", row)
        self.rows.append(remove)
        self.table.setCellWidget(row, 4, remove)
        remove.clicked.connect(lambda: self.delete_row(remove))
        self.name.clear()
        self.email.clear()
        self.qr_code.clear()

    def delete_row(self, widget: CustomDeleteButton):
        for i in range(widget.row + 1, len(self.rows)):
            self.rows[i].row -= 1
        self.rows.remove(widget)
        self.table.removeRow(widget.row)

    def close(self) -> bool:
        self.rows = []
        for row in range(self.table.rowCount()):
            self.table.removeRow(row)
        self.table.setRowCount(0)
        self.table.clear()
        return super().close()


class DeleteLecture(CustomDeleteButton):
    def __init__(self, text, bg, row, signal, **kwargs):
        super().__init__(text, bg, row)
        self.pk = row
        self.signal = signal
        self.bg = bg;
        self.lecture_name = kwargs.get('lecture', '')
        self.clicked.connect(self.delete_lecture)

    def delete_lecture(self):
        self.setStyleSheet("")
        self.widget = QMessageBox.question(self, "Prompt", f"Deleting This Lecture Will Delete All Of It's Attendance Records, Are You Sure You Want To Delete {self.lecture_name}?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)
        if self.widget == QMessageBox.StandardButton.Yes:
            delete_lecture(self.pk)
        self.setStyleSheet(f"background-color: {self.bg}")
        self.signal.emit()


class LecturesWindow(QWidget):
    HEADERS = ["Name", "Course", "Duration", "N. Of Weeks", "Stage", "Teacher", "Assistant", "Is Lab",
               "Associated Lecture", "Actions"]
    signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.cols = [0, 0, 0, 0, 0, 0, 0, 0]
        self.rows = []
        self.vbox = QVBoxLayout()
        self.form = QFormLayout()
        self.lecture_name = QLineEdit()
        self.course = QComboBox()
        self.course.addItems(['Course 1', 'Course 2'])
        self.duration = CustomTimeSpinBox()
        self.week = QSpinBox()
        self.week.setRange(0, 20)
        self.stage = QComboBox()
        self.lectures = get_lectures_info()
        self.stage.addItems(get_stages())
        self.teacher = QComboBox()
        self.teacher.addItems(get_teachers_names())
        self.assistant = QComboBox()
        self.assistant.addItems([""] + list(get_teachers_names()))
        self.is_lab = QCheckBox()
        self.is_lab.setChecked(False)
        self.theories = QComboBox()
        self.theories.addItems(get_theories_lectures())
        self.theories.setHidden(True)
        self.form.addRow("Name:", self.lecture_name)
        self.lecture_name.setMaximumWidth(200)
        self.form.addRow("Course:", self.course)
        self.form.addRow("N. Of Weeks", self.week)
        self.form.addRow("Duration:", self.duration)
        self.form.addRow("Stage:", self.stage)
        self.form.addRow("Instructor:", self.teacher)
        self.form.addRow("Assistant (Optional):", self.assistant)
        self.form.addRow("Lab", self.is_lab)
        self.select_lecture = QLabel("Lecture: ")
        self.select_lecture.setHidden(True)
        self.form.addRow(self.select_lecture, self.theories)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.is_lab.clicked.connect(lambda b: {self.select_lecture.setHidden(not b), self.theories.setHidden(not b)})
        self.vbox.addLayout(self.form)
        self.table = CustomTeacher(len(self.lectures), len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.init_ui()
        self.setLayout(self.vbox)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().sortIndicatorChanged.connect(self.sort_by_column)

    def sort_by_column(self, col):
        if col == len(HEADERS) - 1:
            return
        if self.cols[col]:
            self.table.sortByColumn(col, Qt.SortOrder.DescendingOrder)
            self.cols[col] = 0
        else:
            self.table.sortByColumn(col, Qt.SortOrder.AscendingOrder)
            self.cols[col] = 1

    def init_ui(self):
        # Add
        add_button = QPushButton("Add", clicked=self.save_data)

        self.vbox.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vbox.addWidget(self.table)
        self.init_table()

    def save_data(self):  # YUP
        insert_data(self.lecture_name.text(),
                    self.course.currentText(),
                    unelegant_time(self.duration.text()),
                    int(self.week.text()),
                    int(self.stage.currentIndex() + 1),
                    get_teacher_id(self.teacher.currentText()),
                    get_teacher_id(self.assistant.currentText()), self.is_lab.isChecked(),
                    self.theories.currentText() if self.is_lab.isChecked() else None)
        self.lecture_name.clear()
        self.course.clear()
        self.course.clear()
        self.duration.clear()
        self.stage.clear()
        self.week.clear()
        self.teacher.clear()
        self.assistant.clear()
        self.signal.emit()

    def init_table(self):
        for row, lecture in enumerate(self.lectures):
            name = lecture.name
            course = lecture.course
            weeks = lecture.weeks
            duration = elegant_time(lecture.duration)
            stage = lecture.stage_id
            teacher = get_teacher_name(lecture.user_id)
            assistant = get_teacher_name(lecture.assistant_id)
            is_lab = bool(lecture.is_lab)
            ass = lecture.association_link
            remove = DeleteLecture("Delete", "red", lecture.id, self.signal, lecture=name)
            self.table.add_row((name, course, duration, weeks, stage, teacher, assistant, is_lab, ass), (remove,))

    def delete_row(self, pk):
        delete_lecture(pk)
        self.signal.emit()


class CustomTimeSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 96)
        self.setWrapping(True)
        self.setSingleStep(1)
        self.setDisplayIntegerBase(10)

    def textFromValue(self, value):
        hours = value // 4
        minutes = (value % 4) * 15
        return "{:d}:{:02d}".format(hours, minutes)

    def valueFromText(self, text):
        parts = text.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        value = hours * 4 + minutes // 15
        return value

    def stepBy(self, steps):
        value = self.value()
        hours = value // 4
        minutes = (value % 4) * 15
        step_minutes = self.singleStep() * 15

        if steps > 0:
            minutes += step_minutes
            if minutes >= 60:
                hours += 1
                minutes -= 60
        elif steps < 0:
            minutes -= step_minutes
            if minutes < 0:
                hours -= 1
                minutes += 60

        value = hours * 4 + minutes // 15

        if value > self.maximum():
            value = self.minimum() + (value - self.maximum() - 1)
        elif value < self.minimum():
            value = self.maximum() - (self.minimum() - value - 1)

        self.setValue(value)


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("Fusion")
    window = LecturesWindow()
    window.show()
    app.exec()


class CoupleButtons(QWidget):
    def __init__(self, btn1: QPushButton, btn2: QPushButton):
        super().__init__()
        self.btn1 = btn1
        self.btn2 = btn2
        self.btn2.setMaximumWidth(100)
        self.btn1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # set policy for btn1
        self.btn2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # set policy for btn2
        layout = QHBoxLayout()
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class NewPassword(QWidget):
    def __init__(self, user_id, user_name):
        super().__init__()
        self.setWindowTitle("Rest Password")
        self.user_id = user_id
        self.user_name = user_name
        vbox = QFormLayout()
        title = QLabel(f"Reset Password for {user_name}")
        title.setFont(QFont("Arial", 18, weight=2))
        self.line = PasswordEdit()
        submit = QPushButton("Change")
        submit.clicked.connect(self.submit_pressed)
        vbox.addRow("New Password: ", self.line)
        vbox.addWidget(submit)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(vbox)

    def submit_pressed(self):
        if self.line.text():
            reset_password(self.user_id, hash_sha(self.line.text()))
        self.close()


class ReportButton(QPushButton):
    def __init__(self, text, stage):
        super().__init__(text)
        self.stage = stage
        self.clicked.connect(self.send_report)

    def send_report(self):
        self.widget = QMessageBox.question(self, "Prompt",
                                           f"Are you sure?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)
        if self.widget == QMessageBox.StandardButton.Yes:
            time_now = datetime.now().strftime("%Y-%m-%d %H%M%S")
            emails = ';'.join(get_students_emails(self.stage))
            name = f"students_version_{time_now}.xlsx"
            student_report(get_attendances(self.stage), output=name)
            sending_email(emails, name)


class AdminReport(QPushButton):
    def __init__(self, text, stage):
        super().__init__(text)
        self.stage = stage
        self.clicked.connect(self.send_report)

    def send_report(self):
        self.widget = QMessageBox.question(self, "Prompt",
                                           f"Are you sure?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)
        if self.widget == QMessageBox.StandardButton.Yes:
            time_now = datetime.now().strftime("%Y-%m-%d %H%M%S")
            emails = ';'.join(get_teachers_by_stage(self.stage))
            name = f"instructors_version_{time_now}.xlsx"
            make_admin_report(self.stage, output=name)
            sending_email(emails, name)


class DeleteAttButton(QPushButton):
    def __init__(self, text, stage_id):
        super().__init__(text)
        self.stage = stage_id
        self.clicked.connect(self.btn_clicked)

    def btn_clicked(self):
        self.widget = QMessageBox.question(self, "Prompt",
                                           f"Are you sure?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.No)
        if self.widget == QMessageBox.StandardButton.Yes:
            delete_attendances(self.stage)

class ReportWindow(QWidget):
    signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        self.setup_tabs()

        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)

    def setup_tabs(self):
        for i in range(1, 5):
            tab = QWidget()
            vbox = QVBoxLayout()

            export_button = AdminReport('Admin Report', i)
            export_button.setFixedWidth(150)
            # export_button.setStyleSheet("QPushButton { background-color: #01579b; color: white; padding: 12px;}")
            report_button = ReportButton('Report', i)
            report_button.setFixedWidth(150)
            # report_button.setStyleSheet("QPushButton { background-color: #ff5722; color: white; padding: 12px;}")
            delete_button = DeleteAttButton("Delete Attendance Records", i)
            vbox.addSpacing(20)
            vbox.addWidget(export_button, alignment=Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(report_button, alignment=Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignCenter)
            vbox.addStretch()
            tab.setLayout(vbox)
            self.tab_widget.addTab(tab, f'Stage {i}')


if __name__ == '__main__':
    x = AdmiralWindow('Hello', get_users())
