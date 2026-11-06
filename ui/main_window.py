
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton,
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt


# Custom draggable title bar
class TitleBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = None
        self.setFixedHeight(32)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.window().frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if (
            event.buttons() & Qt.MouseButton.LeftButton
            and self.drag_position is not None
        ):
            self.window().move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

    def mouseReleaseEvent(self, event):
        self.drag_position = None


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Rounded frameless window
        self.setWindowTitle("PySide6 Calculator")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )
        self.setFixedSize(350, 500)

        self.first_number = None
        self.operator = None
        self.waiting_for_second = True

        # Main container
        container = QWidget()
        container.setObjectName("container")

        container.setStyleSheet("""
            QWidget#container {
                background-color: #e3dada;
                border: 1px solid #444444;
                border-radius: 30px;
            }
        """)

        self.setCentralWidget(container)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(12, 10, 12, 12)
        main_layout.setSpacing(10)

        # Custom title bar
        title_bar = TitleBar(container)
        title_layout = QHBoxLayout(title_bar)

        title_label = QLabel("Adder")
        title_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        title_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
        """)

        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # Minimize button
        minimize_button = QPushButton("—")
        minimize_button.setFixedSize(28, 26)
        minimize_button.clicked.connect(self.showMinimized)

        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(28, 26)
        close_button.clicked.connect(self.close)

        for button in [minimize_button, close_button]:
            
        # Minimize button - Blue hover
            minimize_button.setStyleSheet("""
            QPushButton {
                color: black;
                background: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
            }
        """)

        # Close button - Red hover
        close_button.setStyleSheet("""
            QPushButton {
                color: black;
                background: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
            }
        """)


        title_layout.addWidget(minimize_button)
        title_layout.addWidget(close_button)

        main_layout.addWidget(title_bar)

        # Calculator display
        self.label = QLabel("0")

        self.label.setAlignment(
            Qt.AlignmentFlag.AlignRight |
            Qt.AlignmentFlag.AlignVCenter
        )

        self.label.setStyleSheet("""
            font-size: 32px;
            padding: 15px;
            border-radius: 12px;
            background-color: #eeeeee;
            color: black;
        """)

        main_layout.addWidget(self.label)

        # Calculator buttons
        buttons = [
            "7", "8", "9", "/",
            "4", "5", "6", "*",
            "1", "2", "3", "-",
            "C", "0", ".", "+",
            "="
        ]

        positions = [
            (1, 0), (1, 1), (1, 2), (1, 3),
            (2, 0), (2, 1), (2, 2), (2, 3),
            (3, 0), (3, 1), (3, 2), (3, 3),
            (4, 0), (4, 1), (4, 2), (4, 3),
            (5, 0, 1, 4)
        ]

        grid = QGridLayout()
        grid.setSpacing(8)

        for button_text, position in zip(buttons, positions):

            button = QPushButton(button_text)
            button.setMinimumSize(60, 55)

            if button_text == "C":
                color = "#9e1010"
                hover_color = "#c0392b"
            else:
                color = "#333333"
                hover_color = "#555555"

            button.setStyleSheet(f"""
                QPushButton {{
                    font-size: 22px;
                    border-radius: 15px;
                    background-color: {color};
                    color: white;
                }}

                QPushButton:hover {{
                    background-color: {hover_color};
                }}
            """)

            button.clicked.connect(
                lambda checked=False, text=button_text:
                self.handle_button(text)
            )

            grid.addWidget(button, *position)

        main_layout.addLayout(grid)

    # Handle button clicks
    def handle_button(self, text):

        if text == "C":
            self.label.setText("0")
            self.first_number = None
            self.operator = None
            self.waiting_for_second = True
            return

        if text.isdigit():

            if self.waiting_for_second or self.label.text() == "Error":
                self.label.setText(text)
                self.waiting_for_second = False

            else:
                current = self.label.text()
                self.label.setText(
                    text if current == "0" else current + text
                )

        elif text == ".":

            if self.waiting_for_second:
                self.label.setText("0.")
                self.waiting_for_second = False

            elif "." not in self.label.text():
                self.label.setText(self.label.text() + ".")

        elif text in ["+", "-", "*", "/"]:

            if self.label.text() == "Error":
                return

            if self.operator is not None and not self.waiting_for_second:
                self.calculate()

            self.first_number = float(self.label.text())
            self.operator = text
            self.waiting_for_second = True

        elif text == "=":

            if (
                self.operator is not None
                and self.first_number is not None
                and not self.waiting_for_second
            ):
                self.calculate()

    # Perform calculations
    def calculate(self):

        second_number = float(self.label.text())

        try:
            if self.operator == "+":
                result = self.first_number + second_number

            elif self.operator == "-":
                result = self.first_number - second_number

            elif self.operator == "*":
                result = self.first_number * second_number

            elif self.operator == "/":
                result = self.first_number / second_number

            if result.is_integer():
                result = int(result)

            self.label.setText(str(result))

        except ZeroDivisionError:
            self.label.setText("Error")

        self.first_number = None
        self.operator = None
        self.waiting_for_second = True
