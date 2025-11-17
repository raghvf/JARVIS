import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-GuyNeural")   #en-US-AriaNeural

# ---------------------------
# Convert text to speech audio file
# ---------------------------
async def TextToAudioFile(text: str) -> None:
    file_path = r"Data\speech.mp3"

    # Delete existing speech file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate speech audio
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+9%')
    await communicate.save(file_path)

# ---------------------------
# Play generated audio using pygame
# ---------------------------
def TTS(Text: str, func=lambda r=None: True):
    try:
        # Generate speech file
        asyncio.run(TextToAudioFile(Text))

        # Initialize pygame and play
        pygame.mixer.init()
        pygame.mixer.music.load(r"Data\speech.mp3")
        pygame.mixer.music.play()

        # Wait while playing
        while pygame.mixer.music.get_busy():
            if func() is False:
                pygame.mixer.music.stop()
                break
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error in TTS: {e}")

    finally:
        try:
            func(False)
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Error in cleanup: {e}")

# ---------------------------
# Smart Speech Manager
# ---------------------------
def TextToSpeech(Text: str, func=lambda r=None: True):
    Data = str(Text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    # If long text — speak first part and hint about rest
    if len(Data) > 4 and len(Text) >= 250:
        preview = ". ".join(Data[:2]) + ". " + random.choice(responses)
        TTS(preview, func)
    else:
        TTS(Text, func)

# ---------------------------
# Main Loop
# ---------------------------
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        TextToSpeech(user_input)
