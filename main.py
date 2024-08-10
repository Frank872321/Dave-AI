import threading
import speech_recognition as sr
import pyttsx3
import wikipedia
import datetime
import pyjokes
import google.generativeai as genai
import smtplib
import os
import webbrowser as web
import customtkinter as ctk
from youtube_search import YoutubeSearch
from newsapi import NewsApiClient
from AppOpener import open
import env
import time

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Configure Google Generative AI
genai.configure(api_key=env.gemini_api)

# News API setup
newsapi = NewsApiClient(api_key=env.news_api)

# Utility functions
def speak(query):
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    print(query)
    engine.say(query)
    engine.runAndWait()

def obtain_prompt():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:
        you = r.recognize_google(audio, language="vi-VN")
        print(you)
        return you
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    return ""

def send_email(my_email, password, recipient, msg):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email, to_addrs=recipient, msg=msg)

# Main Functions
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon")
    else:
        speak("Good Evening")

def conversation_with_gemini(prompt):
    def run_conversation():
        model = genai.GenerativeModel('gemini-1.0-pro-latest')
        response = model.generate_content(prompt)
        gemini_text = response.text

        # Create a new bubble without clearing any previous content
        bubble = ctk.CTkFrame(bubble_frame, corner_radius=15, fg_color="#555555")
        label = ctk.CTkLabel(bubble, text="", text_color="#ffffff", wraplength=250, justify="left")
        label.pack(padx=10, pady=5)
        bubble.pack(anchor="w", padx=10, pady=5)

        # Speak the response in a separate thread to keep UI responsive
        threading.Thread(target=speak, args=(gemini_text,)).start()
        # Simulate typing effect
        full_text = ""
        for char in gemini_text:
            full_text += char
            label.configure(text=full_text)
            app.update_idletasks()
            time.sleep(0.0438)  # Adjust the speed of the typing effect


    # Run the conversation in a separate thread to keep the UI responsive
    threading.Thread(target=run_conversation).start()

def read_wikipedia():
    speak("What do you want to hear?")
    text = obtain_prompt()
    if text:
        results = wikipedia.summary(text).split('\n')
        speak(results[0])
        for result in results[1:]:
            speak("Do you want to hear more?")
            text = obtain_prompt()
            if "yes" not in text:
                break
            else:
                speak(result)

def open_apps():
    speak("What do you want to open?")
    name = obtain_prompt()
    if name:
        open(name, match_closest=True, throw_error=False)

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
    speak(now.strftime("%H hours %M minutes"))

def tell_dates():
    now = datetime.datetime.now()
    d2 = now.strftime("%B %d, %Y")
    speak(d2)

def play_song():
    speak('What do you want to search?')
    mysong = obtain_prompt()
    if mysong:
        result = YoutubeSearch(mysong, max_results=1).to_dict()
        if result:
            url = 'https://www.youtube.com' + result[0]['url_suffix']
            web.open(url)
            speak('Your video is open now')

def open_fec_edu_vn():
    speak("What website do you want to open?")
    domain = obtain_prompt()
    if domain:
        web.open(domain)

def handle_send_email():
    speak("What should I say?")
    create_chat_bubble("What should I say?", is_user=False)

    # Capture the user's input for the email content
    def capture_email_content():
        msg = user_input.get().strip()
        if msg:
            send_email(env.gmail_id, env.gmail_password, env.gmail_id, msg)
            speak("Your email has been sent!")
            create_chat_bubble("Your email has been sent!", is_user=False)
            user_input.delete(0, ctk.END)
            
            # Reset the send button to the original command after sending the email
            send_button.configure(command=send_message)
        else:
            speak("Message is empty. Please try again.")
            create_chat_bubble("Message is empty. Please try again.", is_user=False)

    # Rebind the Send button to send the email after the user types the message
    send_button.configure(command=capture_email_content)

def handle_message(message):
    if "hello" in message.lower():
        speak("Hello")
        create_chat_bubble("Hello", is_user=False)
    elif "send email" in message.lower():
        handle_send_email()
    elif "time" in message.lower():
        tell_times()
    elif "date" in message.lower():
        tell_dates()
    elif "joke" in message.lower():
        speak(pyjokes.get_joke())
    elif "wikipedia" in message.lower():
        read_wikipedia()
    elif "open website" in message.lower():
        open_fec_edu_vn()
    elif "play song" in message.lower():
        play_song()
    elif "open app" in message.lower():
        open_apps()
    elif "help" in message.lower():
        help_me()
    else:
        # Use Gemini if no keywords match
        conversation_with_gemini(message)

# UI Setup
def create_chat_bubble(text, is_user=True):
    bubble_color = "#00aaff" if is_user else "#555555"
    text_color = "#ffffff"

    bubble = ctk.CTkFrame(bubble_frame, corner_radius=15, fg_color=bubble_color)
    label = ctk.CTkLabel(bubble, text=text, text_color=text_color, wraplength=250, justify="left")
    label.pack(padx=10, pady=5)

    bubble.pack(anchor="e" if is_user else "w", padx=10, pady=5)
    canvas.yview_moveto(1.0)

def send_message():
    message = user_input.get()
    if message:
        create_chat_bubble(message, is_user=True)
        threading.Thread(target=handle_message, args= message)
        user_input.delete(0, ctk.END)

if __name__ == "__main__":
    # Initialize the main window
    app = ctk.CTk()
    app.title("Chat UI with Left Sidebar")
    app.geometry("600x500")

    # Set the theme (dark, light, or system)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    # Left frame (sidebar)
    left_frame = ctk.CTkFrame(app, width=180, height=500, corner_radius=10)
    left_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="ns")

    contact_label = ctk.CTkLabel(left_frame, text="Contacts", text_color="white", font=("Arial", 16))
    contact_label.pack(pady=10)

    for i in range(5):
        contact_button = ctk.CTkButton(left_frame, text=f"Contact {i+1}")
        contact_button.pack(pady=5, padx=10, fill="x")

    # Right frame (main chat UI)
    right_frame = ctk.CTkFrame(app, width=380, height=500, corner_radius=10)
    right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Chat display area inside the right frame
    chat_frame = ctk.CTkFrame(right_frame, width=360, height=400, corner_radius=10)
    chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Create a canvas to hold the chat bubbles
    canvas = ctk.CTkCanvas(chat_frame, width=360, height=380)
    canvas.pack(side="left", fill="both", expand=True)

    # Scrollbar for the chat window
    scrollbar = ctk.CTkScrollbar(chat_frame, orientation="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame inside the canvas where chat bubbles will be placed
    bubble_frame = ctk.CTkFrame(canvas, corner_radius=10)
    bubble_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=bubble_frame, anchor="nw")

    # User input area inside the right frame
    user_input = ctk.CTkEntry(right_frame, width=300, height=30, corner_radius=10)
    user_input.pack(padx=(10, 5), pady=(5, 10), side="left")

    # Send button inside the right frame
    send_button = ctk.CTkButton(right_frame, text="Send", command=send_message, corner_radius=10)
    send_button.pack(padx=(0, 10), pady=(5, 10), side="right")

    # Start the main loop
    app.mainloop()
