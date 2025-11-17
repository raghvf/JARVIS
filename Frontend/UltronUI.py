from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
)
from PyQt6.QtGui import QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt6.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# ====== Environment Setup ======
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Ultron")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

# ====== Helper Functions ======
def AnswerModifier(Answer):
    return '\n'.join([line for line in Answer.split('\n') if line.strip()])

def QueryModifier(Query):
    q = Query.strip()
    if not q:
        return q
    q_lower = q.lower()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    is_question = any(q_lower.startswith(w + " ") or q_lower == w for w in question_words)
    if q[-1] not in ".!?":
        q = q + ("?" if is_question else ".")
    else:
        if is_question and q[-1] != "?":
            q = q[:-1] + "?"
        elif not is_question and q[-1] != ".":
            q = q[:-1] + "."
    return q.capitalize()

def SetMicrophoneStatus(Command):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(os.path.join(TempDirPath, 'Mic.data'), "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    try:
        with open(os.path.join(TempDirPath, 'Mic.data'), "r", encoding='utf-8') as file:
            Status = file.read()
    except FileNotFoundError:
        Status = "False"
    return Status

def SetAssistantStatus(Status):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(os.path.join(TempDirPath, 'Status.data'), "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    try:
        with open(os.path.join(TempDirPath, 'Status.data'), "r", encoding='utf-8') as file:
            Status = file.read()
    except FileNotFoundError:
        Status = ""
    return Status

def MicButtonInitialialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphicsDirPath, Filename)

def TempDirectoryPath(Filename):
    return os.path.join(TempDirPath, Filename)

def ShowTextToScreen(Text):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(os.path.join(TempDirPath, 'Responses.data'), "w", encoding='utf-8') as File:
        File.write(Text)

# ====== Core Widgets ======
class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 40, 100)
        layout.setSpacing(0)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.Shape.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

        text_color = QColor(255, 0, 0)  # red text
        text_format = QTextCharFormat()
        text_format.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_format)

        # Animated AI GIF
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie_path = GraphicsDirectoryPath('UltronCore.gif')
        if os.path.exists(movie_path):
            movie = QMovie(movie_path)
            movie.setScaledSize(QSize(480, 270))
            self.gif_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
            self.gif_label.setMovie(movie)
            movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: red; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)

        # Scroll styling
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: red;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        path = TempDirectoryPath('Responses.data')
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding='utf-8') as file:
                messages = file.read()
        except Exception:
            messages = ""
        if not messages or len(messages) <= 1:
            return
        if str(old_chat_message) == str(messages):
            return
        self.add_message(message=messages, color='red')
        old_chat_message = messages

    def SpeechRecogText(self):
        path = TempDirectoryPath('Status.data')
        if not os.path.exists(path):
            self.label.setText("")
            return
        try:
            with open(path, "r", encoding='utf-8') as file:
                messages = file.read()
        except Exception:
            messages = ""
        self.label.setText(messages)

    def add_message(self, message, color='red'):
        cursor = self.chat_text_edit.textCursor()
        block_format = QTextBlockFormat()
        block_format.setTopMargin(10)
        block_format.setLeftMargin(10)
        char_format = QTextCharFormat()
        char_format.setForeground(QColor(color))
        cursor.setBlockFormat(block_format)
        cursor.setCharFormat(char_format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen = QApplication.primaryScreen().geometry()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 150)

        # --- Ultron Core Animation ---
        core_path = GraphicsDirectoryPath("UltronCore.gif")
        if not os.path.exists(core_path):
            core_path = "UltronCore.gif"   # fallback
        self.core_movie = QMovie(core_path)
        self.core_movie.setScaledSize(QSize(480, 480))

        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setMovie(self.core_movie)
        self.core_movie.start()
        content_layout.addWidget(self.gif_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Mic Icon
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toggled = GetMicrophoneStatus() != "True"
        self.load_icon(GraphicsDirectoryPath('Mic_on.png' if self.toggled else 'Mic_off.png'), 60, 60)
        self.icon_label.mousePressEvent = self.toggle_icon
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status Label
        self.label = QLabel("")
        self.label.setStyleSheet("color: red; font-size:16px; margin-bottom:0;")
        content_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(content_layout)
        self.setFixedHeight(screen.height())
        self.setFixedWidth(screen.width())
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)

    def SpeechRecogText(self):
        path = TempDirectoryPath('Status.data')
        if not os.path.exists(path):
            self.label.setText("")
            return
        try:
            with open(path, "r", encoding='utf-8') as file:
                messages = file.read()
        except Exception:
            messages = ""
        self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path) if os.path.exists(path) else QPixmap()
        new_pixmap = pixmap.scaled(width, height) if not pixmap.isNull() else QPixmap()
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialialed()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen = QApplication.primaryScreen().geometry()
        layout = QVBoxLayout()
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen.height())
        self.setFixedWidth(screen.width())

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        home_button = QPushButton("Home")
        home_button.setStyleSheet("color: red; background-color:black; border:1px solid red;")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        chat_button = QPushButton("Chat")
        chat_button.setStyleSheet("color: red; background-color:black; border:1px solid red;")
        chat_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        close_button = QPushButton("X")
        close_button.setStyleSheet("color:white; background-color:red; font-weight:bold;")
        close_button.clicked.connect(self.closeWindow)

        title = QLabel(f"⚡ {Assistantname.upper()} SYSTEMS ONLINE ⚡")
        title.setStyleSheet("color: red; font-size:18px; background-color:black;")
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(home_button)
        layout.addWidget(chat_button)
        layout.addWidget(close_button)
        self.setLayout(layout)

    def closeWindow(self):
        par = self.parent()
        if par:
            par.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        screen = QApplication.primaryScreen().geometry()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.setStyleSheet("background-color: black;")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
