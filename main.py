import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
import os
from openai import OpenAI
from gtts import gTTS
import pygame
import time
import aiohttp
import asyncio
#from openai.error import RateLimitError

engine = pyttsx3.init()
newsapi = "news_api"
API_KEY = "whether_api"

def speak_old(text):    
    engine.say(text)
    engine.runAndWait()  # This is necessary to ensure the speech is processed

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3') 

    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load the MP3 file
    pygame.mixer.music.load('temp.mp3')

    # Play the MP3 file
    pygame.mixer.music.play()

    # Keep the program running until the music stops playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3") 
async def fetch_weather(city, API_KEY):
    """Fetch weather information for the given city."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            #print(f"Requesting URL: {url}")  # Debugging URL 
            async with session.get(url) as response:
                #print(f"Response status: {response.status}")
                if response.status == 200:
                    try:
                        data = await response.json()  # Parse JSON response
                        #print(f"Response data: {data}")
                        weather = data['weather'][0]['description']
                        temp = data['main']['temp']
                        print(f"The weather in {city} is {weather} with a temperature of {temp} degrees Celsius.")
                        speak(f"The weather in {city} is {weather} with a temperature of {temp} degrees Celsius.")
                    except Exception as json_err:
                        print(f"Error parsing JSON: {json_err}")
                        speak("Sorry, I encountered an error while processing the weather data.")
                else:
                    data = await response.json()  # Parse the error response
                    error_message = data.get("message", "Unknown error")
                    print(f"Error fetching weather: {error_message}")
                    speak(f"Sorry, I couldn't find weather information for {city}.")
    except Exception as err:
        print(f"An error occurred while fetching the weather data: {err}")

def aiProcess(command):
    client = OpenAI(api_key="chatgpt api",
    )
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud. Give short responses please"},
        {"role": "user", "content": command}
        ]
        )
    return completion.choices[0].message.content
   #except RateLimitError:
       # print("Rate limit exceeded. Waiting before retrying...")
       # time.sleep(5)  # Wait for 5 seconds before retrying
       # return aiProcess(command)  # Retry the operation'''
       
def process_command(r,c):
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
    elif c.startswith("play"):
        song = c.lower().split(" ")[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)
    elif c.startswith("temp") :
        speak("Which Location")
        with sr.Microphone() as source:
            audio = r.listen(source,timeout=6,phrase_time_limit=5)
        loc = r.recognize_google(audio)
        print(loc)
        asyncio.run(fetch_weather(loc, API_KEY))        
    elif "khabar" in c.lower():
        r = requests.get(f"https://newsapi.org/v2/everything?q=apple&from=2024-10-09&to=2024-10-09&sortBy=popularity&apiKey={newsapi}")
        if r.status_code == 200:
            # Parse the JSON response
            data = r.json()
            
            # Extract the articles
            articles = data.get('articles', [])
            
            # Print the headlines
            for article in articles:
                speak(article['title'])

    else:
        # Let OpenAI handle the request
        output = aiProcess(c)
        speak(output) 


if __name__ == "__main__":
    speak("Initializing Jarvis")
    while True:
        #Listen For The Wake Word Jarvis
        #Obtain From Microphone
        r = sr.Recognizer()
       

        try:
            with sr.Microphone() as source:
                print("Listening")
                audio = r.listen(source,timeout=3,phrase_time_limit=1)
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            Word = r.recognize_google(audio)
            print(Word)
            if(Word.lower() == "jarvis"):
                speak("Ya")
                print("Active Jarvis...")
                with sr.Microphone() as source:
                    audio = r.listen(source,timeout=6)
                command = r.recognize_google(audio)
                print(command)
                process_command(r,command)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
