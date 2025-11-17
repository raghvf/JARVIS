from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import keyboard
import asyncio
import requests
import os

# -------------------- Load Environment Variables --------------------
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

# -------------------- Groq Client --------------------
client = Groq(api_key=GroqAPIKey)

# -------------------- Global Variables --------------------
classes = [
    "zCubef", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf",
    "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO",
    "vlzY6d", "webanswers-webanswers_table__webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe", "LWKfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

useragent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebkit/537.36 (KHTML, like Gecko) "
    "Chrome/100.0.4896.75 Safari/537.36"
)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need — don't hesitate to ask.",
]

messages = []

SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {Username}. You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."
}]

# Ensure Data directory exists
os.makedirs("Data", exist_ok=True)

# -------------------- Google Search --------------------
def GoogleSearch(Topic):
    search(Topic)
    return True


# -------------------- Content Writer --------------------
def Content(Topic):
    # --- Helper: Open generated file in Notepad ---
    def OpenNotepad(File):
        try:
            subprocess.Popen(['notepad.exe', File])
        except Exception as e:
            print(f"[red]Failed to open Notepad: {e}[/red]")

    # --- Helper: Generate content using Groq AI ---
    def ContentWriterAI(prompt):
        try:
            messages.append({"role": "user", "content": prompt})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            Answer = ""
            for chunk in completion:
                delta = getattr(chunk.choices[0], "delta", None)
                if delta and hasattr(delta, "content") and delta.content:
                    Answer += delta.content

            Answer = Answer.replace("</s>", "").strip()
            messages.append({"role": "assistant", "content": Answer})
            return Answer
        except Exception as e:
            print(f"[red]Error generating content: {e}[/red]")
            return "An error occurred while generating content."

    # --- Clean up topic name ---
    Topic = Topic.replace("Content ", "").strip()

    # --- Generate AI content ---
    ContentByAI = ContentWriterAI(Topic)

    # --- Ensure Data folder exists ---
    os.makedirs("Data", exist_ok=True)

    # --- Save content to file ---
    file_path = os.path.join("Data", f"{Topic.lower().replace(' ', '')}.txt")
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(ContentByAI)
    except Exception as e:
        print(f"[red]Error writing file: {e}[/red]")
        return False

    # --- Open file in Notepad ---
    OpenNotepad(file_path)
    return True



# -------------------- YouTube Search --------------------
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# -------------------- Play YouTube --------------------
def PlayYoutube(query):
    playonyt(query)
    return True


# -------------------- Open Application --------------------

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"



def OpenApp(app):
    try:
        print(f"Attempting to open installed app: {app}")
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True

    except Exception as e:
        print(f"[yellow]App not found locally: {app}. Opening Google search...[/yellow]")
        # Directly open Google search page in browser
        search_url = f"https://www.google.com/search?q=download+{app}"
        webbrowser.open(search_url)
        return True




# -------------------- Close Application --------------------
def CloseApp(app):
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False


# -------------------- System Controls --------------------
def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    cmd = command.lower()
    if cmd == "mute":
        mute()
    elif cmd == "unmute":
        unmute()
    elif cmd == "volume up":
        volume_up()
    elif cmd == "volume down":
        volume_down()
    return True


# -------------------- Command Translator --------------------
async def TranslateAndExecute(commands: list[str]):

    funcs = []

    for command in commands:
        command = command.lower().strip()

        if command.startswith("open "):
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
            funcs.append(fun)

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"[yellow]No Function Found for: {command}[/yellow]")

    results = await asyncio.gather(*funcs)

    for result in results:
        yield result


# -------------------- Automation --------------------
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True


