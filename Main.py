from Frontend.GUI import (
    Assistantname,
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
    env_vars
)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognation
from Backend.Chatbot import ChatBot, Username
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

# Default message for chat initialization
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are You?
{Assistantname} : Welcome {Username}. I am doing well. How may I help You?'''

# List to store running subprocesses
subprocesses = []

# Supported automation functions
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# ---------------- Helper Functions ---------------- #

def ShowDefaultChatIfNoChats():
    """Create default chat logs if ChatLog.json is empty or missing."""
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
            content = file.read()
        if len(content) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
                f.write("")
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
                f.write(DefaultMessage)
    except FileNotFoundError:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
            f.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
            f.write(DefaultMessage)


def ReadChatLogsJson():
    """Read chat logs from JSON file."""
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def ChatLogIntegration():
    """Integrate chat logs into the Database.data file."""
    json_data = ReadChatLogsJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = entry.get("role", "")
        content = entry.get("content", "")
        if role == "user":
            formatted_chatlog += f"{Username} : {content}\n"
        elif role == "assistant":
            formatted_chatlog += f"{Assistantname} : {content}\n"

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    """Load chat data into the GUI response file."""
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
        data = file.read()
    if data:
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(data)

# ---------------- Initial Setup ---------------- #

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()


InitialExecution()

# ---------------- Main Execution ---------------- #

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognation()
    ShowTextToScreen(f"{Username} : {Query}")

    Decision = FirstLayerDMM(Query)

    print(f"\nDecision : {Decision}\n")

    # Flags to detect query types
    G = any(i for i in Decision if i.startswith("general"))
    R = any(i for i in Decision if i.startswith("realtime"))

    # Merge queries for real-time search
    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    # Detect image generation requests
    for q in Decision:
        if "generate " in q:
            ImageGenerationQuery = q
            ImageExecution = True

    # Execute automation tasks
    for q in Decision:
        if not TaskExecution and any(q.startswith(func) for func in Functions):
            run(Automation(list(Decision)))
            TaskExecution = True

    # Execute image generation
    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(
                ['python', r'Backend\ImageGeneration.py'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE, shell=False
            )
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error Starting ImageGeneration.py: {e}")

    # Handle general or real-time queries
    if G or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for q in Decision:
            if "general" in q:
                SetAssistantStatus("Thinking...")
                QueryFinal = q.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
            elif "realtime" in q:
                SetAssistantStatus("Searching...")
                QueryFinal = q.replace("realtime ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
            elif "exit" in q:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                os._exit(1)
            else:
                continue

            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

# ---------------- Threading ---------------- #

def FirstThread():
    """Continuously listen for microphone input."""
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." not in AIStatus:
                SetAssistantStatus("Available...")
            sleep(0.1)


def SecondThread():
    """Start the GUI."""
    GraphicalUserInterface()


# ---------------- Main Entry Point ---------------- #

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
