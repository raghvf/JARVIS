import datetime
from json import load, dump
from dotenv import dotenv_values
from groq import Groq
from googlesearch import search
import requests
import os


# ========== ENVIRONMENT VARIABLES ==========
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)


# ========== BASIC SYSTEM PROMPT ==========
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}, 
which has real-time up-to-date information from the internet.

*** Provide answers in a professional way. Use full stops, commas, question marks, and proper grammar. ***
*** Just answer the question from the provided data in a professional and concise manner. ***
"""


# ========== INITIAL CHAT LOG SETUP ==========
if not os.path.exists("Data"):
    os.makedirs("Data")

if not os.path.exists("Logs"):
    os.makedirs("Logs")

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
    messages = []


# ========== ERROR LOGGER ==========
def log_error(message):
    with open("Logs/errors.log", "a", encoding="utf-8") as log:
        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{time_now}] {message}\n")


# ========== GOOGLE SEARCH FUNCTION ==========
def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
        Answer = f"The search result for '{query}' are:\n[start]\n"
        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
        Answer += "[end]"
        return Answer

    except requests.exceptions.ConnectTimeout:
        msg = f"Connection timed out while searching for '{query}'."
        log_error(msg)
        return f"⚠️ Unable to connect to Google. {msg}"

    except Exception as e:
        msg = f"Google Search failed for '{query}': {str(e)}"
        log_error(msg)
        return f"⚠️ An error occurred while performing Google Search: {str(e)}"


# ========== CLEANING FUNCTION ==========
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


# ========== BASE SYSTEM CONTEXT ==========
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]


# ========== REAL-TIME INFO (DATE & TIME) ==========
def Information():
    current_date_time = datetime.datetime.now()
    return (
        f"Use this real-time information if needed.\n"
        f"Day: {current_date_time.strftime('%A')}\n"
        f"Date: {current_date_time.strftime('%d')}\n"
        f"Month: {current_date_time.strftime('%B')}\n"
        f"Year: {current_date_time.strftime('%Y')}\n"
        f"Time: {current_date_time.strftime('%H')} hours, "
        f"{current_date_time.strftime('%M')} minutes, "
        f"{current_date_time.strftime('%S')} seconds.\n"
    )


# ========== MAIN REAL-TIME SEARCH ENGINE ==========
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load chat history
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": f"{prompt}"})

    # Perform search with error handling
    google_data = GoogleSearch(prompt)
    SystemChatBot.append({"role": "system", "content": google_data})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        SystemChatBot.pop()
        return AnswerModifier(Answer=Answer)

    except Exception as e:
        msg = f"Groq API call failed: {str(e)}"
        log_error(msg)
        return f"⚠️ Failed to get AI response: {str(e)}"


# ========== MAIN LOOP ==========
if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query: ")
        if prompt.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        print(RealtimeSearchEngine(prompt))
