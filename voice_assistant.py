import time
import requests
import json
import speech_recognition as sr
import wikipedia
import datetime
import webbrowser
import os
import wolframalpha
# https://developer.wolframalpha.com/portal/myapps/index.html
import pyttsx3
# https://pyttsx3.readthedocs.io/en/latest/engine.html
from pathlib import Path

# Set engine to Pyttsx3 for text-to-speech. Sapi5 is a Microsoft speech application platform interface.
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# Setting the voice id - voices[0] is male voice, voices[1] is female
engine.setProperty('voice', voices[0].id) 

# Speak given text
def speak(audio):
    # Queues commands to speak
    engine.say(audio)
    # Blocks while processing currently queued commands - returns when all commands queued prior emptied from queue
    engine.runAndWait()

# Greet user
def greeting():

    hour = int(datetime.datetime.now().hour)
    helper_name = ("Gertrude the Terrible")

    if hour >= 0 and hour < 12:
        speak("Good Morning Your Excellency !")
    elif hour >= 12 and hour < 18: 
        speak("Good Afternoon You Animal !")
    else:
        speak("Good Evening Beloved !")

    speak(f"I am here to assist you, my name is {helper_name}")

# Get user name and welcome user
def get_name():

    speak("What should I call you?")

    user_name = get_voice_input()
    print(f"Welcome {user_name}")
    speak(f"Welcome my dearest {user_name}")
    speak("How can I help you today?")

    return user_name

# Listen for voice input and return query unless exception raised
def get_voice_input():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        # Listens for 1 second to calibrate for ambient noise
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        # Represents minimum length of silence will register as end of a phrase
        recognizer.pause_threshold = 1
        # Records single phrase from source - has optional timeout parameter
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        # Use Google Web Speech API - https://wicg.github.io/speech-api/
        query = recognizer.recognize_google(audio, language="en-in")
        print(f"You said: {query}\n")

    except Exception as e:
        print(e)
        print("I'm sorry, I don't understand.")
        return "None"

    return query


if __name__ == "__main__":
    # Clears any commands before execution of this file
    clear = lambda: os.system("cls")
    clear()
    # Greet user and get user's name
    greeting()
    user_name = get_name()
    # Create Wolfram Alpha client with api key
    wolf_api_id = "P3VJ6A-97RR5EGKVT"
    client = wolframalpha.Client(wolf_api_id)

    while True:

        query = get_voice_input().lower()
        search_query = query.replace(" ", "+")

        # Create new file and add text to it
        if "new file" in query:
            speak("What should I name your file?")
            file_name = get_voice_input().replace(" ", "_")

            with open(f"{file_name}.txt", "w") as text:
                speak("What would you like to write?")
                transcript = get_voice_input()
                text.write(transcript)
                speak(f"I have added the following: {query}")

        # Open new file and add text to it
        elif "open file" or "transcribe" in query:
            query = ""

            speak("Here are the files you can open")
            # Get filepath and save any text files in a list
            path = Path(__file__).parent.absolute()
            files = [x for x in os.listdir(path) if x.endswith(".txt")]
            
            # If there are text files in the folder, get name of folder to open and open it
            if files:
                print(files)
                speak(files)
                speak("Which file do you want opened?")
                file_name = get_voice_input()

                for file in files:
                    if file_name in file:
                        with open(file, "a+") as document:
                            speak(f"I've opened {file}. Would you like me to read its contents?")
                            answer = get_voice_input()
                            if "yes" in answer:
                                existing_text = document.read()
                                print(existing_text)
                                speak(existing_text)

                            speak(f"Would you like to add to this file?")

                            answer = get_voice_input()
                            if "yes" in answer:
                                speak(f"OK I'm listening.")
                                transcription = get_voice_input()
                                document.write(transcription)
                                speak(f"Your text has been added.")
            else:
                speak("There are currently no text files in this folder.")

        elif "wikipedia" in query:
            speak("Searching Wikipedia...")
            query = query.replace("wikipedia", "")
            # Returns first 4 sentences of result
            results = wikipedia.summary(query, sentences = 4)
            print(results)
            speak(results)

        elif "open google" in query:
            speak("Taking you to Google")
            webbrowser.open("google.com")

        elif "google" in query:
            # Remove unnecessary text from query
            search_query = search_query.replace("google", "")     
            search_query = search_query.replace("search", "")            
            speak("Searching Google")
            webbrowser.open(f"google.com/search?q={search_query}")

        elif "youtube" in query:
            # Remove unnecessary text from query
            search_query = search_query.replace("youtube", "")      
            search_query = search_query.replace("search", "")            
            speak("Taking you to Youtube\n")
            webbrowser.open(f"youtube.com/results?search_query={search_query}")            

        elif "open stack overflow" in query:
            speak("Taking you to Stack Overflow")
            webbrowser.open("stackoverflow.com")  

        # Use the Wolfram Alpha API to answer math queries
        elif "calculate" in query:
            # Remove unnecessary text from query
            index = query.lower().split().index("calculate")
            query = query.split()[index + 1:]
            response = client.query(" ".join(query))
            # Respond with iterable
            answer = next(response.results).text
            print(answer)
            speak(f"{query} is {answer}")
            
        # Use the Wolfram Alpha API to answer general queries
        # elif "what is" in query or "who is" in query or "what are" in query:
        elif len([x for x in ["what is", "who is", "what are" ] if x in query]) > 0:
            response = client.query(query)
            answer = next(response.results).text
            print(answer)
            speak(f"The answer to your query is {answer}")
            
        elif "what time" in query:
            str_time = datetime.datetime.now().strftime("%H %M %Z")   
            speak(f"The time is {str_time} {user_name}")

        elif "don't listen" in query or "stop listening" in query:
            speak(f"How many seconds should I stop listening for?")
            sleep_time = int(get_voice_input())
            if sleep_time:
                speak(f"Very well.")
                time.sleep(sleep_time)
            speak(f"Hello my friend, I am back!")

        elif "exit" in query:
            speak(f"Goodbye {user_name}, may the force be with you")
            exit()

