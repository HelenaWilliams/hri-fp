# How to run this file: fp_woz.py <misty_ip> <participant_name>
# Final Project Team: HARDcore Gamers!

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import websocket
import sys, os, time
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
    def __init__(self):
        global on, off

        # Creates the window for the tkinter interface
        self.root = tk.Tk()
        self.root.geometry("900x900")
        self.root.title("Misty GUI")

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
        self.speak_button = tk.Button(self.text_frame, wraplength=300, text="Speak", height=3, font=("Ariel",10), command=lambda: self.speak(self.textbox.get()))
        self.speak_button.grid(row=0, column=1, padx=5, pady=0)

        # Add clear button to clear the text in text entry box
        self.erase_button = tk.Button(self.text_frame, wraplength=300, text="Clear", height=3, font=("Ariel",10), command=self.text_erase)
        self.erase_button.grid(row=0, column=2, padx=5, pady=0)

        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.columnconfigure(0, weight=1)

        # Pre-scripted Messages
        self.greet = tk.Button(self.buttonframe, wraplength=100, text="Greeting", font=("Ariel",10), bg="yellow", command=lambda m="greet": self.speech_button(m), height=5)
        self.greet.grid(row=1, column=0, sticky=tk.W+tk.E)

        self.win = tk.Button(self.buttonframe, wraplength=100, text="Victory", font=("Ariel",10), bg="yellow", command=lambda m="win": self.speech_button(m), height=5)
        self.win.grid(row=2, column=0, sticky=tk.W+tk.E)
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
        self.r1 = tk.Button(self.buttonframe, wraplength=100, text="C1", font=("Ariel",10), bg="yellow", command=lambda m="1": self.speech_button(m), height=5)
        self.r1.grid(row=3, column=0, sticky=tk.W+tk.E)

        self.r2 = tk.Button(self.buttonframe, wraplength=100, text="C2", font=("Ariel",10), bg="yellow", command=lambda m="2": self.speech_button(m), height=5)
        self.r2.grid(row=3, column=1, sticky=tk.W+tk.E)

        self.r3 = tk.Button(self.buttonframe, wraplength=100, text="C3", font=("Ariel",10), bg="yellow", command=lambda m="3": self.speech_button(m), height=5)
        self.r3.grid(row=3, column=2, sticky=tk.W+tk.E)

        self.r4 = tk.Button(self.buttonframe, wraplength=100, text="C4", font=("Ariel",10), bg="yellow", command=lambda m="4": self.speech_button(m), height=5)
        self.r4.grid(row=3, column=3, sticky=tk.W+tk.E)

        self.r5 = tk.Button(self.buttonframe, wraplength=100, text="C5", font=("Ariel",10), bg="yellow", command=lambda m="5": self.speech_button(m), height=5)
        self.r5.grid(row=3, column=4, sticky=tk.W+tk.E)

        self.r6 = tk.Button(self.buttonframe, wraplength=100, text="C6", font=("Ariel",10), bg="yellow", command=lambda m="6": self.speech_button(m), height=5)
        self.r6.grid(row=3, column=5, sticky=tk.W+tk.E)

        self.r7 = tk.Button(self.buttonframe, wraplength=100, text="C7", font=("Ariel",10), bg="yellow", command=lambda m="7": self.speech_button(m), height=5)
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


        #TODO: Add more customized buttons to drive misty, play audio, move arms, change led lights, change displayed image, and etc.

        # Add a line separator
        self.separator = ttk.Separator(self.root, orient='horizontal')
        self.separator.pack(fill='x', pady=20)

        # Section 4: Video Stream
        self.label = tk.Label(self.root, text="Live Video Stream (No Audio)", font=("Ariel", 18))
        self.label.pack(padx=20, pady=10)

        # Add a placeholder for video streaming
        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        # Start stream
        self.start_video_stream()

        self.root.mainloop()

    def speak(self, phrase):
        if(len(phrase) > 0):
            print(f"Speak: {phrase}")
            # refer to robot commands in RobotCommands.py - https://github.com/MistyCommunity/Python-SDK/blob/main/mistyPy/RobotCommands.py
            # or in the Misty API documentation - https://lessons.mistyrobotics.com/python-elements/misty-python-api
            misty.speak(phrase)
        else:
            print("Error! No text in text box!")

    def action(self, phrase):
        print(f"Action: {phrase}")
        # refer to robot commands in RobotCommands.py - https://github.com/MistyCommunity/Python-SDK/blob/main/mistyPy/RobotCommands.py
        # or in the Misty API documentation - https://lessons.mistyrobotics.com/python-elements/misty-python-api

        # TODO: edit the following action and add 3 more to handle your customized nonverbal behaviors and robot reactions (e.g., surprise)
        # if phrase == "move_head_1":
        #     misty.move_head(-15, 0, 0, 0)
        if phrase == "change_face":
            misty.display_image("e_Disgust.jpg", 1)
            time.sleep(5)
            misty.display_image("e_Joy.jpg", 1)
        if phrase == "whee":
            misty.play_audio("s_Ecstacy2.wav")
        if phrase == "orange_lights":
            misty.change_led(255, 155, 0)
            time.sleep(5)
            misty.change_led(0, 0, 255)
        if phrase == "nod":
            misty.move_head(-40, 0, 0, 100)
            time.sleep(0.5)
            misty.move_head(26, 0, 0, 100)
            time.sleep(0.5)
            misty.move_head(-40, 0, 0, 100)
            time.sleep(0.5)
            misty.move_head(0, 0, 0, 100)
        if phrase == "shake":
            for i in range(2):
                misty.move_head(0, 0, -50, 100)
                time.sleep(0.5)
                misty.move_head(0, 0, 50, 100)
                time.sleep(0.5)
            misty.move_head(0, 0, 0, 100)

    def switch(self):
        global is_human
        
        # Determine is on or off
        if is_human:
            self.on_button.config(image = off)
            is_human = False
        else:
            self.on_button.config(image = on)
            is_human = True         

    def speech_button(self, phrase):
        output = "Error! Invalid phrase!"
        if is_human:
            #print("Human")
            if phrase == "greet":
                output = "Hello "+name+"! My name is Misty, and I'm a robot! I'm here today to play some games of Connect-4 with you. Ready to start? "
            elif phrase == "win":
                output = "I win! Thanks for playing. Could you reset the board for me?"
            else:
                output = "Hmm… Could you play my next move in Column " + phrase + "?"
        else:
            #print("Robot")
            if phrase == "greet":
                output = "Greetings, "+name+". I am Misty II, an advanced open robotics platform. I am here today to complete multiple rounds of Connect-4 with you. Are you prepared to begin?"
            elif phrase == "win":
                output = "Play session concluded. Please reset the board."
            else:
                output = "Please place a red piece in Column " + phrase + "."
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

    def start_video_stream(self):
        # Make sure misty's camera service is enabled
        response = misty.enable_camera_service()
        print("misty.enable_camera_service response code:", response.status_code) # this should show 200

        # Configure the preferred video stream settings
        # Notice: This port number can be changed video live stream is crashed
        # This port number must be between 1024 and 65535, default is 5678.
        self.video_port = 5680
        try:
            # Start video streaming
            response = misty.start_video_streaming(
                port=self.video_port, 
                rotation=90, 
                width=640, 
                height=480, 
                quality=60, 
                overlay=False
            )
            
            print("misty.start_video_streaming response code:", response.status_code) # this should show 200

        except Exception as e:
            print(f"Error starting video stream: {e}")
        
        # Establish WebSocket connection to stream video data
        video_ws_url = f"ws://{ip_address}:{self.video_port}"
        print(video_ws_url)

        def on_message(ws, message):
            try:
                # Process the incoming message (video frame)
                image = Image.open(BytesIO(message))
                image = image.resize((320, 240))  # Resize as needed
                photo = ImageTk.PhotoImage(image)
                self.video_label.configure(image=photo)
                self.video_label.image = photo  # Keep a reference to the image
            except Exception as e:
                print(f"Error processing video frame: {e}")

        def on_error(ws, error):
            print(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("WebSocket closed")

        def on_open(ws):
            print("WebSocket connection opened")

        # Create a WebSocket app and set up event handlers
        ws_app = websocket.WebSocketApp(
            video_ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        # Run the WebSocket app in a separate thread
        ws_thread = threading.Thread(target=ws_app.run_forever, daemon=True)
        ws_thread.start()


# Run the GUI
if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python misty_introduction.py <Misty's IP Address> <participant name>")
        sys.exit(1)

    ip_address = sys.argv[1]
    name = sys.argv[2]
    misty = Robot(ip_address)

    MistyGUI()