from PyQt6.QtCore import Qt, QEventLoop, QEasingCurve, QVariant, pyqtSlot, QVariantAnimation, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor, QPalette
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect

start_color = QColor(220, 0, 0, 55)
end_color = QColor(220, 0, 0, 255)


class LoginPage(QWidget):
    success_signal = pyqtSignal(bool)

    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        self.success_signal.connect(self.success_login)
        self.incorrect_label = AnimationLabel("""<p>Incorrect credentials</p>""")
        self.success_label = QLabel("""<p color=green>Success!</p>""")
        self.incorrect_label.setObjectName("incorrect")
        self.frame = QFrame()
        self.frame.setFixedSize(400, 320)
        self.main_layout = QVBoxLayout()
        self.account_box = QVBoxLayout()
        self.initialize()

    def initialize(self):
        self.setWindowTitle("Tech App")
        self.setAutoFillBackground(True)
        self.main_layout.setContentsMargins(10, 30, 0, 0)
        logo_label = QLabel()
        p = QPixmap("assets/main_logo.png")
        p.setDevicePixelRatio(2.6)
        logo_label.setPixmap(p)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.main_layout.addWidget(logo_label)

        # Account Details
        main_label = QLabel("""<h1>Account Details</h1>""")
        main_label.setFont(QFont("Lato", 10))
        main_label.setObjectName("accountDetails")
        self.account_box.addWidget(main_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # Incorrect credentials
        self.incorrect_label.setFont(QFont("Lato", 10))
        self.account_box.addWidget(self.incorrect_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.incorrect_label.hide()
        # Success Label
        self.success_label.hide()
        self.account_box.addWidget(self.success_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Username
        username_label = QLabel("""<p>Username: </p>""")
        username_label.setFont(QFont("Lato", 16))
        username_label.setObjectName("usernameLabel")
        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Enter username here")
        self.username_entry.setFixedSize(200, 40)
        self.username_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.account_box.addWidget(username_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.account_box.addWidget(self.username_entry, alignment=Qt.AlignmentFlag.AlignHCenter)
        # Password
        password_label = QLabel("""<p>Password: </p>""")
        password_label.setFont(QFont("Lato", 16))
        password_label.setObjectName("passwordLabel")
        self.password_entry = PasswordEdit(show_visibility=True)
        self.password_entry.setPlaceholderText("Enter password here")
        self.password_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.password_entry.setFixedSize(200, 40)
        self.account_box.addWidget(password_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.account_box.addWidget(self.password_entry, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.account_box.addStretch()
        # Login Button
        login_button = QPushButton("Login", clicked=self.login)
        login_button.setShortcut("Return")
        self.account_box.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        login_button.setFixedSize(100, 40)

        self.main_layout.addStretch(1)
        self.frame.setObjectName("frame")
        self.frame.setLayout(self.account_box)
        self.frame.setAutoFillBackground(True)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(100)
        self.frame.setGraphicsEffect(shadow)
        self.frame.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.main_layout.addWidget(self.frame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch(2)
        self.setLayout(self.main_layout)

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        self.signal.emit(username, password)

    def success_login(self, is_success):
        if is_success is False:
            self.incorrect_show()
        else:
            self.incorrect_label.hide()
            self.success_label.show()
            self.username_entry.setEnabled(False)
            self.password_entry.setEnabled(False)
            self.destroy(True, True)

    def resizeEvent(self, a0) -> None:
        size = a0.size()
        self.frame.setFixedSize(max(int(size.width() / 3), 400), max(int(size.height() / 5), 300))

    def incorrect_show(self):
        self.incorrect_label.show()
        self.incorrect_label.startAnimation()


class PasswordEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.visibleIcon = QIcon("assets/eye.svg")
        self.hiddenIcon = QIcon("assets/hidden.svg")

        self.setEchoMode(QLineEdit.EchoMode.Password)

        if kwargs.get('show_visibility', False):
            # Add the password hide/shown toggle at the end of the edit box.
            self.password_action = self.addAction(
                self.visibleIcon,
                QLineEdit.ActionPosition.TrailingPosition
            )
            self.password_action.triggered.connect(self.clicked)

        self.password_shown = False

    def clicked(self):
        if not self.password_shown:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self.password_shown = True
            self.password_action.setIcon(self.hiddenIcon)
        else:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_shown = False
            self.password_action.setIcon(self.visibleIcon)


class AnimationLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.setAccessibleName("AnimationLabel")
        self.animation = QVariantAnimation()
        self.animation.valueChanged.connect(self.changeColor)

    @pyqtSlot(QVariant)
    def changeColor(self, color):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, color)
        self.setPalette(palette)

    def startFadeIn(self):
        self.animation.stop()
        self.animation.setStartValue(start_color)
        self.animation.setEndValue(end_color)
        self.animation.setDuration(350)
        self.animation.setEasingCurve(QEasingCurve.Type.InBack)
        self.animation.start()

    def startAnimation(self):
        self.startFadeIn()
        loop = QEventLoop()
        self.animation.finished.connect(loop.quit)
        loop.exec()
