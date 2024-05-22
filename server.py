import tkinter as tk
import pyaudio
import wave
import socket
import threading


def record_audio():
    global recording, frames
    stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    frames = []

    while recording:
        data = stream.read(chunk)
        frames.append(data)

    stream.close()

def start_recording():
    global recording
    recording = True
    start_button.config(state=tk.DISABLED)  # Disable the start button
    threading.Thread(target=record_audio).start()

def stop_recording():
    global recording
    recording = False
    start_button.config(state=tk.NORMAL)  # Re-enable the start button after stopping
    save_audio()

def save_audio():
    with wave.open("output.wav", "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

def upload_audio():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("128.2.204.249", 40001))
        with open("output.wav", "rb") as f:
            audio_data = f.read()
            sock.sendall(audio_data)

def on_closing():
    if recording:
        stop_recording()
    window.destroy()

# Audio settings
chunk = 1024
format = pyaudio.paInt16
channels = 1  # Mono audio
rate = 44100
recording = False
frames = []

audio = pyaudio.PyAudio()

# Setting up the GUI
window = tk.Tk()
window.title("Audio Recorder")
# Keep window always on top
window.attributes('-topmost', True)
frame = tk.Frame(window)
frame.pack()

start_button = tk.Button(frame, text="Start Recording", command=start_recording)
start_button.pack(side=tk.LEFT)

stop_button = tk.Button(frame, text="Stop Recording", command=stop_recording)
stop_button.pack(side=tk.LEFT)

upload_button = tk.Button(frame, text="Upload Recording", command=upload_audio)
upload_button.pack(side=tk.LEFT)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
