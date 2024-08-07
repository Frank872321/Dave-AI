import speech_recognition as sr
import pyttsx3
import wikipedia
import datetime
import pyjokes
import google.generativeai as genai
import os
import pathlib
from IPython.display import display
from IPython.display import Markdown
import requests, json
import smtplib
import env
from newsapi import NewsApiClient
from AppOpener import open
import datetime
import webbrowser as web
from youtubesearchpython import VideosSearch
from youtube_search import YoutubeSearch
import customtkinter 
from time import *

define_ai_prompt = "You are an AI assistant, also known as Homemade AI create by Frank as a side project."
genai.configure(api_key=env.gemini_api)
newsapi = NewsApiClient(api_key=env.news_api)
you =""
engine = pyttsx3.init()
wasted_hoursforreal = 8

def obtain_prompt():
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        you = r.recognize_google(audio, language="vi-VN")
        print(you)
        return you
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

def speak(query):
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    print(query)
    engine.say(query)
    engine.runAndWait()

def wishMe():
    # this is a good morning/afternoon/evening function
    hour = int(datetime.datetime.now().hour)
    if hour>= 0 and hour<12:
        speak("Good Morning")
    elif hour>= 12 and hour<18:
        speak("Good Afternoon")   
    else:
        speak("Good Evening") 
   
def conversation_with_gemini(prompt):
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(prompt)
    print("##################Generating, please wait##################")
    speak(response.text)

def get_weather():
    # Enter your API key here
    api_key = env.weather_api

    # base_url variable to store url
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # Give city name
    city_name = input("Enter city name : ")

    # complete_url variable to store
    # complete url address
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name

    # get method of requests module
    # return response object
    response = requests.get(complete_url)

    # json method of response object 
    # convert json format data into
    # python format data
    x = response.json()

    # Now x contains list of nested dictionaries
    # Check the value of "cod" key is equal to
    # "404", means city is found otherwise,
    # city is not found
    if x["cod"] != "404":

        # store the value of "main"
        # key in variable y
        y = x["main"]

        # store the value corresponding
        # to the "temp" key of y
        current_temperature = y["temp"]

        # store the value corresponding
        # to the "pressure" key of y
        current_pressure = y["pressure"]

        # store the value corresponding
        # to the "humidity" key of y
        current_humidity = y["humidity"]

        # store the value of "weather"
        # key in variable z
        z = x["weather"]

        # store the value corresponding 
        # to the "description" key at 
        # the 0th index of z
        weather_description = z[0]["description"]

        # print following values
        speak(" Temperature (in celsius) is " +
                        str(format(current_temperature-273.15, ".2f")) +
            "\n atmospheric pressure (in hPa unit) is " +
                        str(current_pressure) +
            "\n humidity (in percentage) is " +
                        str(current_humidity) +
            "\n description is " +
                        str(weather_description))

    else:
        print(" City Not Found ")
def send_email(my_email, password, email, msg):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        connection.ehlo_or_helo_if_needed()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email,
                            to_addrs=email,
                            msg= msg)

def read_wikipedia():
    speak("What do you want to hear")
    text = obtain_prompt()
    results = wikipedia.summary(text).split('\n')
    speak(results[0])
    for result in results[1:]:
        speak("Do you want to here more?")
        text = obtain_prompt()
        if "yes" not in text:
            break
        else:
            speak(result)
def open_apps():
    speak("What do you want to open")
    name = obtain_prompt()
    open(name, match_closest=True, throw_error= False)
def help_me():
    speak("""I can do these things to help you: 
          1. Tell you the time
          2. Tell you what is today
          3. Tell you a joke
          4. Help you send message
          5. Tell you about the weather
          6. Talk to you something on Wikipedia
          7. Talk to you like a normal person by Gemini
          8. Open the web for you
          9. Search YouTube and play music
          10. Open application""")
def tell_times():
    now = datetime.datetime.now()
    speak(now.strftime("%H hours %M minute"))

def tell_dates():
    now = datetime.datetime.now()
    d2 = now.strftime("%B %d, %Y")
    speak(d2)

def play_song():
    speak('What do you want to search')
    mysong = obtain_prompt()
    while True:
        result = YoutubeSearch(mysong, max_results=10).to_dict()
        if result:
            break
    url = 'https://www.youtube.com' + result[0]['url_suffix']
    web.open(url)
    speak('Your video is open now')

def open_fec_edu_vn():
    speak("What website do you want to open")
    domain = obtain_prompt()
    web.open(domain)

# funcion ends now, main funcion and ui starts here
if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
    customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green 
    app = customtkinter.CTk()  # create CTk window like you do with the Tk window
    app.geometry("340x400")
    frame = customtkinter.CTkFrame(master=app, width=200, height=400)
    frame1 = customtkinter.CTkFrame(master=app, width=500, height=400)
    app.grid_rowconfigure(weight = 1, index = 0)
    app.grid_columnconfigure(weight= 1, index=1)
    frame.grid(row = 0, column = 0, sticky = "nsew")
    frame1.grid(row = 0, column = 1, sticky = "nsew")
    app.mainloop()