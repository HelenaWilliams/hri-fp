# How to run this file: fp_woz.py <misty_ip> <participant_name>
# Final Project Team: HARDcore Gamers!
from openai import OpenAI
import json, os, requests, socket, sys, time
from dotenv import load_dotenv
from datetime import datetime
from time import sleep
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import threading
import random

###This part could be different for everyone### 
sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'Python-SDK'))

# sys.path.append(os.path.join(os.path.dirname(__file__), 'Python-SDK'))
###This part could be different for everyone###
from mistyPy.Robot import Robot
from mistyPy.Events import Events

is_human = True
on = -1
off = -1

class MistyGUI:
    #def __init__(self):
    def __init__(self, ip_address, name):
        self.misty_ip = ip_address
        self.name = name
        self.misty = Robot(ip_address)
        global on, off
        
        # load the environment variables from the .env file
        load_dotenv()

        # initialize the OpenAI client for TTS with the OPEN_AI_API_KEY environment variable
        open_ai_api_key = os.getenv('OPEN_AI_API_KEY')
        if not open_ai_api_key:
            raise ValueError("Please set the OPEN_AI_API_KEY environment variable.")
        self.openai_client = OpenAI(api_key=open_ai_api_key)

        self.speech_file_path_local = path = os.path.join(os.path.dirname(__file__), 'robot_speech_files/speech.wav')
        local_ip_address = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in\
 [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        self.speech_file_path_for_misty = 'http://' + local_ip_address + ':8000/robot_speech_files/speech.wav'
        self.volume = 30

        # Creates the window for the tkinter interface
        self.root = tk.Tk()
        self.root.geometry("900x900")
        self.root.title("Misty GUI")
        self.accent = "en-GB-Wavenet-B"

        # Define Our Images
        on = tk.PhotoImage(file = "on.png")
        off = tk.PhotoImage(file = "off.png")

        # Section 1: Timer

        # Creates a stopwatch at the top of the screen
        self.label = tk.Label(self.root, text="Timer", font=("Ariel",20))
        self.label.pack(padx=20,pady=0)

        # Time variables
        self.time_elapsed = 0
        self.running = False

        self.time_display = tk.Label(self.root, text="0:00", font=("Ariel", 18))
        self.time_display.pack()

        self.timer_frame = tk.Frame(self.root)
        self.timer_frame.pack(padx=10, pady=5)

        self.starttimer_button = tk.Button(self.timer_frame, text="Start", command=self.start)
        self.starttimer_button.grid(row=0, column=0, padx=5, pady=0)

        self.stoptimer_button = tk.Button(self.timer_frame, text="Stop", command=self.stop)
        self.stoptimer_button.grid(row=0, column=2, padx=5, pady=0)

        self.reset_button = tk.Button(self.timer_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=3, padx=5, pady=0)

        self.update_time()

        # Add a line separator
        self.separator = ttk.Separator(self.root, orient='horizontal')
        self.separator.pack(fill='x', pady=20)

        # Section 2: Speech Control
        self.label = tk.Label(self.root, text="Speech Control Panel", font=("Ariel",18))
        self.label.pack(padx=20,pady=0)

        self.label = tk.Label(self.root, text="Human Mode Toggle", font=("Ariel",12))
        self.label.pack(padx=20,pady=0)

        # Create A Button
        self.on_button = tk.Button(image = on, bd = 0, command = self.switch)
        self.on_button.pack(pady = 10)

        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(padx=10, pady=5)

        self.textbox = tk.Entry(self.text_frame, width=100, font=("Ariel",10))
        self.textbox.grid(row=0, column=0, padx=5, pady=0)

        # Add speak button
        self.speak_button = tk.Button(self.text_frame, wraplength=100, text="Speak", height=3, font=("Ariel",10), command=lambda: self.speak(self.textbox.get()))
        self.speak_button.grid(row=0, column=1, padx=5, pady=0)

        # Add clear button to clear the text in text entry box
        self.erase_button = tk.Button(self.text_frame, wraplength=100, text="Clear", height=3, font=("Ariel",10), command=self.text_erase)
        self.erase_button.grid(row=0, column=2, padx=5, pady=0)

        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.columnconfigure(0, weight=1)

        # Pre-scripted Messages
        self.intro1 = tk.Button(self.buttonframe, wraplength=100, text="Intro 1", font=("Ariel",10), bg="yellow", command=lambda m="intro1": self.speech_button(m), height=5)
        self.intro1.grid(row=1, column=0, sticky=tk.W+tk.E)

        self.intro2 = tk.Button(self.buttonframe, wraplength=100, text="Intro 2", font=("Ariel",10), bg="yellow", command=lambda m="intro2": self.speech_button(m), height=5)
        self.intro2.grid(row=1, column=1, sticky=tk.W+tk.E)

        self.your_turn = tk.Button(self.buttonframe, wraplength=100, text="Your Turn", font=("Ariel",10), bg="yellow", command=lambda m="your_turn": self.speech_button(m), height=5)
        self.your_turn.grid(row=1, column=2, sticky=tk.W+tk.E)

        self.win = tk.Button(self.buttonframe, wraplength=100, text="Victory", font=("Ariel",10), bg="yellow", command=lambda m="win": self.speech_button(m), height=5)
        self.win.grid(row=2, column=0, sticky=tk.W+tk.E)

        self.oops = tk.Button(self.buttonframe, wraplength=100, text="Mistake", font=("Ariel",10), bg="yellow", command=lambda m="oops": self.speech_button(m), height=5)
        self.oops.grid(row=2, column=1, sticky=tk.W+tk.E)

        self.buttonframe.pack(fill='x')
        
        self.goodbye = tk.Button(self.buttonframe, wraplength=100, text="Goodbye", font=("Ariel",10), bg="yellow", command=lambda m="goodbye": self.speech_button(m), height=5)
        self.goodbye.grid(row=2, column=2, sticky=tk.W+tk.E)

        self.buttonframe.pack(fill='x')

        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)
        self.buttonframe.columnconfigure(2, weight=1)
        self.buttonframe.columnconfigure(3, weight=1)
        self.buttonframe.columnconfigure(4, weight=1)
        self.buttonframe.columnconfigure(5, weight=1)
        self.buttonframe.columnconfigure(6, weight=1)

        # Gameplay Buttons
        self.r1 = tk.Button(self.buttonframe, wraplength=100, text="C1", font=("Ariel",10), bg="yellow", command=lambda: self.speech_button("misty_turn", "1"), height=5)
        self.r2 = tk.Button(self.buttonframe, wraplength=100, text="C2", font=("Ariel",10), bg="yellow", command=lambda: self.speech_button("misty_turn", "2"), height=5)
        self.r3 = tk.Button(self.buttonframe, wraplength=100, text="C3", font=("Ariel",10), bg="yellow", command=lambda: self.speech_button("misty_turn", "3"), height=5)
        self.r4 = tk.Button(self.buttonframe, wraplength=100, text="C4", font=("Ariel",10), bg="yellow", command=lambda: self.speech_button("misty_turn", "4"), height=5)
        self.r5 = tk.Button(self.buttonframe, wraplength=100, text="C5", font=("Ariel",10), bg="yellow", command=lambda: self.speech_button("misty_turn", "5"), height=5)
        self.r6 = tk.Button(self.buttonframe, wraplength=100, text="C6", font=("Ariel",10), bg="yellow", command=lambda: self.speech_button("misty_turn", "6"), height=5)
        self.r7 = tk.Button(self.buttonframe, wraplength=100, text="C7", font=("Ariel",10), bg="yellow", command=lambda: self.speech_button("misty_turn", "7"), height=5)
        
        self.r1.grid(row=3, column=0, sticky=tk.W+tk.E)
        self.r2.grid(row=3, column=1, sticky=tk.W+tk.E)
        self.r3.grid(row=3, column=2, sticky=tk.W+tk.E)
        self.r4.grid(row=3, column=3, sticky=tk.W+tk.E)
        self.r5.grid(row=3, column=4, sticky=tk.W+tk.E)
        self.r6.grid(row=3, column=5, sticky=tk.W+tk.E)
        self.r7.grid(row=3, column=6, sticky=tk.W+tk.E)

        self.buttonframe.pack(fill='x')

        # Add a line separator
        self.separator = ttk.Separator(self.root, orient='horizontal')
        self.separator.pack(fill='x', pady=20)

        # Section 3: Action Control
        self.label = tk.Label(self.root, text="Action Control Panel", font=("Ariel",18))
        self.label.pack(padx=20,pady=0)

        self.topbutton_frame = tk.Frame(self.root)
        self.topbutton_frame.pack(padx=10, pady=0)

        self.face_button = tk.Button(self.topbutton_frame, wraplength=300, text="Change Face", height=3, font=("Ariel",10), command=lambda m="change_face": self.action(m))
        self.face_button.grid(row=0, column=0, padx=5, pady=0)

        self.noise_button = tk.Button(self.topbutton_frame, wraplength=300, text="Whee!", height=3, font=("Ariel",10), command=lambda m="whee": self.action(m))
        self.noise_button.grid(row=0, column=1, padx=5, pady=0)

        self.orange_lights = tk.Button(self.topbutton_frame, wraplength=300, text="Orange LED", height=3, font=("Ariel",10), command=lambda m="orange_lights": self.action(m))
        self.orange_lights.grid(row=0, column=2, padx=5, pady=0)

        self.nod = tk.Button(self.topbutton_frame, wraplength=300, text="Nod", height=3, font=("Ariel",10), command=lambda m="nod": self.action(m))
        self.nod.grid(row=0, column=3, padx=5, pady=0)

        self.shake = tk.Button(self.topbutton_frame, wraplength=300, text="Shake Head", height=3, font=("Ariel",10), command=lambda m="shake": self.action(m))
        self.shake.grid(row=0, column=4, padx=5, pady=0)


        ## New gestures

        self.wave = tk.Button(self.topbutton_frame, wraplength=300, text="Wave", height=3, font=("Ariel",10), command=lambda m="wave": self.action(m))
        self.wave.grid(row=1, column=0, padx=5, pady=0)

        self.tilt = tk.Button(self.topbutton_frame, wraplength=300, text="Head Tilt", height=3, font=("Ariel",10), command=lambda m="tilt": self.action(m))
        self.tilt.grid(row=1, column=1, padx=5, pady=0)

        self.shrug = tk.Button(self.topbutton_frame, wraplength=300, text="Shrug", height=3, font=("Ariel",10), command=lambda m="shrug": self.action(m))
        self.shrug.grid(row=1, column=2, padx=5, pady=0)

        self.hop = tk.Button(self.topbutton_frame, wraplength=300, text="Hop", height=3, font=("Ariel",10), command=lambda m="hop": self.action(m))
        self.hop.grid(row=1, column=3, padx=5, pady=0)

        #TODO: Add more customized buttons to drive misty, play audio, move arms, change led lights, change displayed image, and etc.
        self.humanoid_misty_turn = [
            "Hmm… Could you play my next move in Column",
            "Let's see… can you put a yellow piece in ummm… Column",
            "I think I'd like to make my next move in Column",
            "Ooo… can you please play my next move in Column",
            "Okay… I'm thinking Column",
            "Got it! Let's go with Column",
            "Alright, uhh… let's try Column"
            ]

        self.robotic_misty_turn = [
            "Please place a yellow piece in Column",
            "Insert a yellow game token into Column",
            "Execute action: yellow piece in Column",
            "Please deploy my yellow piece to Column",
            "Initiating move sequence- place yellow piece in Column",
            "System decision logged- please place a yellow piece in Column",
            "Please confirm placement of yellow piece in Column"
            ]

        self.humanoid_your_turn = [
            "Your turn! Let's see what you do.",
            "Okay, it's your move now.",
            "Go ahead- your turn to play.",
            "Hmm… I wonder where you'll go next.",
            "Alright! You're up!",
            "Whenever you're ready, it's your turn.",
            "Your move- make it count!"
            ]

        self.robotic_your_turn = [
            "Human turn initiated. Proceed.",
            "It is now your move. Begin.",
            "Awaiting your input.",
            "Please take your turn.",
            "Your move is required.",
            "Begin your turn when prepared.",
            "Insert red piece to continue."
            ]

        self.humanoid_victory = [
            ("I win! Thanks for playing. Could you reset the board for me?", "orange_lights"),
            ("Haha! I won that one! You almost had me though! Could you reset the board?", "celebrate_soft"),
            ("Victory! I guess all that training paid off. Mind resetting the board for the next round?", "double_blink_smile"),
            ("Phew, that was close— nice game! Can you set the board back up?", "smile"),
            ("Oh wow, that was intense! Good game. Let's reset the board so we can play again.", "head_nod_small")
            ]

        self.robotic_victory = [
            "Play session concluded. Please reset the board.",
            "Game sequence complete. Outcome: robot victory. Please reset the board.",
            "Victory achieved. Recalibrating for next session. Please reset the Connect-4 environment.",
            "This match has concluded in my favor. Please restore the game board.",
            "Session result: win recorded. Prepare for subsequent round. Awaiting board reset."
            ]
 
        # Add a line separator
        self.separator = ttk.Separator(self.root, orient='horizontal')
        self.separator.pack(fill='x', pady=20)

        self.root.mainloop()

    def speak(self, phrase):
        self.phrase = phrase
        self.root.after(0, self._generate_speech)

    def _generate_speech(self):
        if is_human: 
            instructions="Speak with a calm and encouraging tone." 
        else: 
            instructions="Speak in a robotic, monotone voice with autotune."
        try:
            with self.openai_client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=self.phrase,
                instructions=instructions
            ) as response:
                response.stream_to_file(self.speech_file_path_local)
            self.root.after(100, self._upload_speech)
        except Exception as e:
            print(f"Speech error: {e}")
    
    def _upload_speech(self):
         try:
            self.misty.delete_audio("speech.mp3")

            with open(self.speech_file_path_local, "rb") as f:
                response = requests.post(
                    f"http://{self.misty_ip}/api/audio",
                    files={'data': ('speech.mp3', f, 'audio/mpeg')},
                    data={'FileName': 'speech.mp3'}
                )

            self.root.after(100, self._play_audio)

         except Exception as e:
            print(f"Upload error: {e}")

    def _play_audio(self):
        try:
            self.misty.play_audio("speech.mp3", volume=self.volume)
        except Exception as e:
            print(f"Playback error: {e}")

    def action(self, phrase):
        print(f"Action: {phrase}")

        if phrase == "change_face":
            self.misty.display_image("e_Disgust.jpg", 1)
            self.root.after(5000, lambda: self.misty.display_image("e_Joy.jpg", 1))

        elif phrase == "whee":
            self.misty.play_audio("s_Ecstacy2.wav")

        elif phrase == "orange_lights":
            self.misty.change_led(255, 155, 0)
            self.root.after(5000, lambda: self.misty.change_led(0, 0, 255))

        elif phrase == "nod":
            steps = [(-40, 0), (26, 0), (-40, 0), (0, 0)]
            for i, (pitch, yaw) in enumerate(steps):
                self.root.after(i * 500, lambda p=pitch, y=yaw: self.misty.move_head(p, 0, y, 100))

        elif phrase == "shake":
            def shake_sequence(step):
                if step < 4:
                    angle = -50 if step % 2 == 0 else 50
                    self.misty.move_head(0, 0, angle, 100)
                    self.root.after(500, lambda: shake_sequence(step + 1))
                else:
                    self.misty.move_head(0, 0, 0, 100)
            shake_sequence(0)

        elif phrase == "double_blink_smile":
            self.misty.display_image("e_Joy.jpg", 1)
            self.misty.change_led(255, 200, 0)
            self.root.after(400, lambda: self.misty.change_led(0, 0, 255))
            self.root.after(1400, lambda: self.misty.display_image("e_DefaultContent.jpg", 1))

        elif phrase == "eye_shift":
            self.misty.move_head(0, -15, -20, 80)
            self.root.after(500, lambda: self.misty.move_head(0, 0, 0, 80))

        elif phrase == "head_nod_small":
            self.misty.move_head(-10, 0, 0, 50)
            self.root.after(500, lambda: self.misty.move_head(0, 0, 0, 50))

        elif phrase == "celebrate_soft":
            self.misty.display_image("e_Joy.jpg", 1)
            self.misty.play_audio("s_Joy3.wav")
            self.root.after(1500, lambda: self.misty.display_image("e_DefaultContent.jpg", 1))

        elif phrase == "smile":
            self.misty.display_image("e_Joy.jpg", 1)
            self.root.after(2000, lambda: self.misty.display_image("e_DefaultContent.jpg", 1))

        elif phrase == "wave":
            def wave_step(step):
                if step == 0:
                    self.misty.move_arms(-89, 0)
                    self.root.after(1000, lambda: wave_step(1))
                elif step == 1:
                    self.misty.move_arms(0, 0)
                    self.root.after(750, lambda: wave_step(2))
                elif step == 2:
                    self.misty.move_arms(-89, 0)
                    self.root.after(750, lambda: wave_step(3))
                elif step == 3:
                    self.misty.move_arms(0, 0)
            wave_step(0)

        elif phrase == "tilt":
            self.misty.move_head(0, 0, 20, 100)
            self.root.after(500, lambda: self.misty.move_head(0, 0, 0, 100))

        elif phrase == "shrug":
            self.misty.move_arms(-60, -60)
            self.root.after(500, lambda: self.misty.move_arms(0, 0))

        elif phrase == "thinking":
            self.misty.display_image("e_ContentLeft.jpg", 1)
            self.misty.play_audio("s_Bored.wav")
            self.root.after(1500, lambda: self.misty.display_image("e_DefaultContent.jpg", 1))

        elif phrase == "hop":
            self.misty.play_audio("s_Joy2.wav")
            self.misty.move_head(-20, 0, 0)
            self.misty.move_arms(-60, -60)
            self.root.after(500, lambda: [
                self.misty.move_head(0, 0, 0),
                self.misty.move_arms(0, 0)
            ])

    def switch(self):
        global is_human
        
        # Determine is on or off
        if is_human:
            self.on_button.config(image = off)
            is_human = False
        else:
            self.on_button.config(image = on)
            is_human = True         

    def speech_button(self, phrase, column=None):
        output = "Error! Invalid phrase!"
        if is_human:
            if phrase == "intro1":
                self.action("wave")
                self.misty.display_image("e_DefaultContent.jpg", 1)
                output = (
                    f"Hi {self.name}! My name is Misty, and I'm a robot! "
                    "I'm here today to play some games of Connect-4 with you. "
                    "I can talk with you, make faces, and celebrate—or get a little grumpy when I lose. "
                    "I can't answer questions about other things, but I'll do my best to keep it fun! "
                    "My arms are too short to play my pieces by myself—can you help me place them on the board?"
                )
            elif phrase == "intro2":
                self.action("nod")
                self.misty.display_image("e_Joy.jpg", 1)
                output = (
                    "Awesome, thank you so much! I think you should play red, which means you go first—whenever you're ready! "
                    "I've been training my whole life for this—hehe."
                )
            elif phrase == "win":
                speech, gesture = random.choice(self.humanoid_victory)
                self.action(gesture)
                output = speech
            elif phrase == "oops":
                self.misty.display_image("e_Surprise.jpg", 1)
                output = "Oh no! I made a mistake—could you undo my last move? Sorry!"
                self.root.after(2000, lambda: self.misty.display_image("e_DefaultContent.jpg", 1))
            elif phrase == "misty_turn":
                self.misty.display_image("e_ContentLeft.jpg", 1)
                gesture = random.choice(["tilt", "thinking", "eye_shift"])
                self.action(gesture)
                output = random.choice(self.humanoid_misty_turn) + f" {column}?"
                self.root.after(500, lambda: self.misty.display_image("e_DefaultContent.jpg", 1))
            elif phrase == "your_turn":
                self.misty.display_image("e_ContentLeft.jpg", 1)
                output = random.choice(self.humanoid_your_turn)
                self.root.after(500, lambda: self.misty.display_image("e_DefaultContent.jpg", 1))
            elif phrase == "goodbye":
                self.misty.display_image("e_Admiration.jpg", 1)
                self.action("wave")
                self.root.after(2000, lambda: self.misty.display_image("e_Joy.jpg", 1))
                output = (
                    f"Thanks for playing, {self.name}! I had a lot of fun, and I hope you did too! "
                    "You gave me a great challenge. You're pretty good, you know… for a human! "
                    "Goodbye for now, but I hope I have the chance to play with you again."
                )
            else:
                output = "Unrecognized phrase."
        else:
            if phrase == "intro1":
                output = (
                    f"Greetings, {self.name}. I am Misty II, an advanced robotics platform. "
                    "I am here to engage in several rounds of Connect-4 with you. "
                    "I can generate speech, display expressions, and respond to game outcomes. "
                    "I cannot answer unrelated questions, but I will follow the game protocols. "
                    "My arms cannot reach the board—can you please assist by placing my pieces for me?"
                )
            elif phrase == "intro2":
                output = (
                    "Acknowledged, thank you for your assistance. You have been assigned red, "
                    "and will take the first turn—begin when ready. My systems are calibrated for optimal performance."
                )
            elif phrase == "win":
                output = random.choice(self.robotic_victory)
            elif phrase == "oops":
                output = "Error. Incorrect move selected. Remove last added piece from board."
            elif phrase == "misty_turn":
                output = random.choice(self.robotic_misty_turn) + f" {column}."
            elif phrase == "your_turn":
                output = random.choice(self.robotic_your_turn)
            elif phrase == "goodbye":
                output = (
                    f"Thank you for participating, {self.name}. Your performance exceeded baseline human metrics. "
                    "Session concluded. I hope we engage in gameplay again soon."
                )
            else:
                output = "Unrecognized phrase."

        self.text_erase()
        self.textbox.insert(0, output)


    def text_box(self):
        print(f"Text: {self.textbox.get()}")
        self.textbox.delete(0, tk.END)
        self.reset()

    def text_erase(self):
        self.textbox.delete(0, tk.END)

    def update_time(self):
        if self.running:
            self.time_elapsed += 1
            self.update_display()
            self.root.after(1000, self.update_time)

    def update_display(self):
        minutes = (self.time_elapsed % 3600) // 60
        seconds = self.time_elapsed % 60
        self.time_display.config(text=f"{minutes:01}:{seconds:02}")

    def start(self):
        if not self.running:
            self.running = True
            self.update_time()

    def stop(self):
        self.running = False

    def reset(self):
        self.running = False
        self.time_elapsed = 0
        self.update_display()

# Run the GUI
if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python misty_introduction.py <Misty's IP Address> <participant name>")
        sys.exit(1)

    ip_address = sys.argv[1]
    name = sys.argv[2]

    #MistyGUI()
    MistyGUI(ip_address, name)