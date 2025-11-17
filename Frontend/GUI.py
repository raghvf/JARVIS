from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
)
from PyQt5.QtGui import QIcon, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat, QPainter
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


def QueryModifier(Query):
    q = Query.strip()
    if not q:
        return q
    q_lower = q.lower()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    # Determine if it is a question (starts with a question word)
    is_question = any(q_lower.startswith(w + " ") or q_lower == w for w in question_words)

    # Normalize ending punctuation
    if q[-1] not in ".!?":
        q = q + ("?" if is_question else ".")
    else:
        # ensure question mark for questions
        if is_question and q[-1] != "?":
            q = q[:-1] + "?"
        elif (not is_question) and q[-1] != ".":
            q = q[:-1] + "."

    return q.capitalize()


def SetMicrophoneStatus(Command):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)


def GetMicrophoneStatus():
    try:
        with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
            Status = file.read()
    except FileNotFoundError:
        Status = "False"
    return Status


def SetAssistantStatus(Status):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)


def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
            Status = file.read()
    except FileNotFoundError:
        Status = ""
    return Status


def MicButtonInitialialed():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'


def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'


def ShowTextToScreen(Text):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as File:
        File.write(Text)


class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 40, 100)
        layout.setSpacing(0)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        # GIF label
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie_path = GraphicsDirectoryPath('Live chatbot.gif')
        if not os.path.exists(movie_path):
            movie_path = GraphicsDirectoryPath('Live chatbot.gif')  # fallback
        movie = QMovie(movie_path) if os.path.exists(movie_path) else None
        max_gif_size_W = 480
        max_gif_size_H = 270
        if movie:
            movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.gif_label.setMovie(movie)
            movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.addWidget(self.gif_label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)  # polling interval (ms) — increased from 5 to 200 for stability

        self.chat_text_edit.viewport().installEventFilter(self)

        self.setStyleSheet(f"""
            QScrollBar:vertical {{
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: white;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: black;
                height: 10px;
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                border:none;
                background: none;
                color:none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
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
        self.add_message(message=messages, color='white')
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

    def add_message(self, message, color='white'):
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
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        movie_path = GraphicsDirectoryPath('Live chatbot.gif')
        if not os.path.exists(movie_path):
            movie_path = GraphicsDirectoryPath('Live chatbot.gif')
        movie = QMovie(movie_path) if os.path.exists(movie_path) else None
        if movie:
            max_gif_size_H = int(screen_width / 16 * 9)
            movie.setScaledSize(QSize())
            gif_label.setMovie(movie)
            movie.start()
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.icon_label = QLabel()
        pixmap_path = GraphicsDirectoryPath('Mic_on.png')
        if not os.path.exists(pixmap_path):
            pixmap_path = GraphicsDirectoryPath('Mic_on.PNG')
        pixmap = QPixmap(pixmap_path) if os.path.exists(pixmap_path) else QPixmap()
        new_pixmap = pixmap.scaled(60, 60) if not pixmap.isNull() else QPixmap()
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.toggled = True
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px ; margin-bottom:0;")

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
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
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color:black")

        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("chat-65.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color:black")

        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet(" background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet(" background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath("Close.png"))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet(" background-color:white")
        close_button.clicked.connect(self.closeWindow)

        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color:black;")

        title_label = QLabel(f" {str(Assistantname).capitalize()} AI   ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color: white")

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        par = self.parent()
        if par:
            par.showMinimized()

    def maximizeWindow(self):
        par = self.parent()
        if not par:
            return
        if par.isMaximized():
            par.showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            par.showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        par = self.parent()
        if par:
            par.close()

    def mousePressEvent(self, event):
        if self.draggable and self.parent():
            # store offset between global mouse pos and window top-left
            self.offset = event.globalPos() - self.parent().frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset and self.parent():
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Frameless flag corrected
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()
