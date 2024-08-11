import threading
import time
import speech_recognition as sr
import pyttsx3
import wikipedia
import datetime
import pyjokes
import google.generativeai as genai
import smtplib
import webbrowser as web
import customtkinter as ctk
from youtube_search import YoutubeSearch
from AppOpener import open
import env

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Configure Google Generative AI
genai.configure(api_key=env.gemini_api)

# Utility functions
def speak(query):
    threading.Thread(target=lambda: engine.say(query) or engine.runAndWait()).start()

def obtain_prompt():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio, language="vi-VN")
    except (sr.UnknownValueError, sr.RequestError) as e:
        print(f"Error with speech recognition: {e}")
        return ""

def send_email(my_email, password, recipient, msg):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email, to_addrs=recipient, msg=msg)

def display_typing_effect(bubble, text, delay=0.03):
    full_text = ""
    for char in text:
        full_text += char
        bubble.configure(text=full_text)
        app.update_idletasks()
        time.sleep(delay)

def handle_conversation(model, prompt, is_wikipedia=False):
    def conversation_task():
        response_text = model.generate_content(prompt).text if not is_wikipedia else wikipedia.summary(prompt).split('\n')[0]
        bubble = create_chat_bubble("", is_user=False)
        display_typing_effect(bubble, response_text)
        speak(response_text)
    threading.Thread(target=conversation_task).start()

def handle_wikipedia_search():
    speak("What do you want to search on Wikipedia?")
    create_chat_bubble("What do you want to search on Wikipedia?", is_user=False)

    def fetch_wikipedia_content():
        search_query = user_input.get().strip()
        if search_query:
            try:
                handle_conversation(wikipedia, search_query, is_wikipedia=True)
            except wikipedia.exceptions.DisambiguationError as e:
                disambiguation_msg = f"The term {search_query} is ambiguous. Suggestions: {e.options[:5]}"
                create_chat_bubble(disambiguation_msg, is_user=False)
                speak(disambiguation_msg)
            except wikipedia.exceptions.PageError:
                error_msg = f"Sorry, no information found on {search_query}."
                create_chat_bubble(error_msg, is_user=False)
                speak(error_msg)
            reset_input()
        else:
            speak("Input is empty. Please try again.")
            create_chat_bubble("Input is empty. Please try again.", is_user=False)

    send_button.configure(command=fetch_wikipedia_content)

def handle_play_song():
    speak("What song do you want to search for?")
    create_chat_bubble("What song do you want to search for?", is_user=False)

    def fetch_song_content():
        song_query = user_input.get().strip()
        if song_query:
            result = YoutubeSearch(song_query, max_results=1).to_dict()
            if result:
                url = 'https://www.youtube.com' + result[0]['url_suffix']
                web.open(url)
                speak('Your video is open now')
                create_chat_bubble("Playing: " + result[0]['title'], is_user=False)
            reset_input()
        else:
            speak("Input is empty. Please try again.")
            create_chat_bubble("Input is empty. Please try again.", is_user=False)

    send_button.configure(command=fetch_song_content)

def handle_open_website():
    speak("What website do you want to open?")
    create_chat_bubble("What website do you want to open?", is_user=False)

    def fetch_website_content():
        domain = user_input.get().strip()
        create_chat_bubble(domain, True)
        if domain:
            web.open(domain)
            speak(f"Opening {domain}")
            create_chat_bubble(f"Opening {domain}", is_user=False)
            reset_input()
        else:
            speak("Input is empty. Please try again.")
            create_chat_bubble("Input is empty. Please try again.", is_user=False)

    send_button.configure(command=fetch_website_content)

def handle_open_apps():
    speak("What application do you want to open?")
    create_chat_bubble("What application do you want to open?", is_user=False)

    def fetch_app_content():
        app_name = user_input.get().strip()
        if app_name:
            open(app_name, match_closest=True, throw_error=False)
            speak(f"Opening {app_name}")
            create_chat_bubble(f"Opening {app_name}", is_user=False)
            reset_input()
        else:
            speak("Input is empty. Please try again.")
            create_chat_bubble("Input is empty. Please try again.", is_user=False)

    send_button.configure(command=fetch_app_content)

def reset_input():
    user_input.delete(0, ctk.END)
    send_button.configure(command=send_message)

def handle_send_email():
    speak("What should I say?")
    create_chat_bubble("What should I say?", is_user=False)

    def capture_email_content():
        msg = user_input.get().strip()
        if msg:
            send_email(env.gmail_id, env.gmail_password, env.gmail_id, msg)
            speak("Your email has been sent!")
            create_chat_bubble("Your email has been sent!", is_user=False)
            reset_input()
        else:
            speak("Message is empty. Please try again.")
            create_chat_bubble("Message is empty. Please try again.", is_user=False)

    send_button.configure(command=capture_email_content)
def help_me():
    help_text = """I can do these things to help you:
                   1. Tell you the time
                   2. Tell you what is today
                   3. Tell you a joke
                   4. Help you send message
                   5. Tell you about the weather
                   6. Talk to you something on Wikipedia
                   7. Talk to you like a normal person by Gemini
                   8. Open the web for you
                   9. Search YouTube and play music
                   10. Open application"""
    threading.Thread(target=speak, args=(help_text,)).start()
def handle_message(message):
    message = message.lower()
    if "hello" in message:
        create_chat_bubble("Hello", is_user=False)
        speak("Hello")
    elif "send email" in message:
        handle_send_email()
    elif "time" in message:
        speak(datetime.datetime.now().strftime("%H hours %M minutes"))
    elif "date" in message:
        speak(datetime.datetime.now().strftime("%B %d, %Y"))
    elif "joke" in message:
        speak(pyjokes.get_joke())
    elif "wikipedia" in message:
        handle_wikipedia_search()
    elif "gemini" in message:
        handle_conversation(genai.GenerativeModel('gemini-1.0-pro-latest'), obtain_prompt())
    elif "open website" in message:
        handle_open_website()
    elif "play song" in message:
        handle_play_song()
    elif "open app" in message:
        handle_open_apps()
    elif "help" in message:
        help_me()
    else:
        handle_conversation(genai.GenerativeModel('gemini-1.0-pro-latest'), message)

# UI Setup
def create_chat_bubble(text, is_user=True):
    bubble_color = "#00aaff" if is_user else "#555555"
    bubble = ctk.CTkLabel(bubble_frame, text=text, text_color="#ffffff", wraplength=250, justify="left", fg_color=bubble_color, corner_radius=15, padx=10, pady=5)
    bubble.pack(anchor="e" if is_user else "w", padx=10, pady=5)
    canvas.yview_moveto(1.0)
    return bubble

def send_message():
    message = user_input.get()
    if message:
        create_chat_bubble(message, is_user=True)
        handle_message(message)
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
