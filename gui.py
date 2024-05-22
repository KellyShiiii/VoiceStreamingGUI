import tkinter as tk
import threading
import pyaudio
import wave
import numpy as np
import zmq
import datetime
import msgpack
import time
import os
from zmq_utils import create_socket, send_payload
import json
from requests import get
# Define a global flag
recording = False

def record_audio(outdir, num_channels, audio_dir, socket, socket2, socket3, audio_output_files, dirs_file, start_button):
    p = pyaudio.PyAudio()
    stream = p.open(
                rate=16000,
                format=p.get_format_from_width(2),
                channels=num_channels,
                input=True,
                frames_per_buffer=1024)

    print('Recording started.')
    global recording
    try:
        while recording:
            data = stream.read(1024, exception_on_overflow=False)
            for i in range(num_channels):
                channel_audio = np.frombuffer(data, dtype=np.int16)[i::num_channels].tobytes()
                audio_output_files[i].writeframes(channel_audio)
                if i == 0:
                    originatingTime = send_payload(socket, "audio", channel_audio)
                    print(f"Channel 0 audio sent at {originatingTime}", len(channel_audio))

    except KeyboardInterrupt:
        print("Recording interrupted by user.")
    finally:
        stop_recording(stream, p, audio_output_files, dirs_file, start_button)

def stop_recording(stream, p, audio_output_files, dirs_file, start_button):
    print('Stopping Recording')
    stream.stop_stream()
    stream.close()
    p.terminate()
    for wf in audio_output_files:
        wf.close()
    dirs_file.close()
    start_button.config(state=tk.NORMAL)
    print('Recording stopped and files closed.')

def stop_recording_using_button(start_button):
    global recording
    recording = False  # Properly set the global flag to False
    print('Recording flag set to stop.')
    # The actual stopping of the stream and cleanup will be handled in the record_audio function once it notices the flag has been set to False.
    # start_button.config(state=tk.NORMAL)  # Re-enable the start button

def start_recording_thread(outdir, num_channels, start_button):
    global recording
    recording = True
    start_button.config(state=tk.DISABLED)

    audio_dir = os.path.join(outdir, "audio", datetime.datetime.now().strftime('%m-%d-%y_%H:%M:%S'))
    os.makedirs(audio_dir, exist_ok=True)
    send_IPs_to_PSI()
    socket = create_socket(ip_address='tcp://*:40001')
    socket2 = create_socket(ip_address='tcp://*:40002')
    socket3 = create_socket(ip_address='tcp://*:40003')

    audio_output_files = []
    dirs_file = open(os.path.join(audio_dir, "doa.txt"), "w")
    for i in range(num_channels):
        wf = wave.open(os.path.join(audio_dir, f"output_channel_{i}.wav"), 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)  # Assuming 16-bit audio
        wf.setframerate(16000)
        audio_output_files.append(wf)

    threading.Thread(target=record_audio, args=(outdir, num_channels, audio_dir, socket, socket2, socket3, audio_output_files, dirs_file, start_button)).start()

def find_my_ip(api_service_ip='https://api.ipify.org'):
    my_ip = get(api_service_ip).content.decode('utf8')
    return my_ip

def share_my_ip_with_psi(my_ip, my_port=40003, psi_server_ip_port="tcp://128.2.204.249:40001"):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    print("Connecting to server...")
    socket.connect(psi_server_ip_port)   # bree
    request = f"tcp://{my_ip}:{my_port}"     # erebor
    payload = {}
    payload['message'] = request
    payload['originatingTime'] = datetime.datetime.utcnow().isoformat()
    print(f"Sending request: {request}")
    socket.send_string(request)
    print(f"Waiting for reply...")
    reply = socket.recv()
    print(f"Received reply: {reply}")

# def send_IPs_to_PSI (): 
#     context = zmq.Context()
#     socket = context.socket(zmq.REQ)

#     print("Connecting to server...")
#     socket.connect("tcp://128.2.204.249:40001")   # bree
#     time.sleep(1)

#     request = json.dumps({"sensorVideoText":"tcp://128.2.212.138:40000", "sensorAudio": "tcp://128.2.212.138:40001", "sensorDOA": "tcp://128.2.212.138:40002", "sensorVAD": "tcp://128.2.212.138:40003"})   # erebor"
#     # request = "tcp://128.2.149.108:40003"
#     # request = "tcp://23.227.148.141:40003"

#     # Send the request
#     payload = {}
#     payload['message'] = request
#     payload['originatingTime'] = datetime.datetime.utcnow().isoformat()
#     print(f"Sending request: {request}")
#     socket.send_string(request)

#     #  Get the reply
#     reply = socket.recv()
#     print(f"Received reply: {reply}")

def send_IPs_to_PSI():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    print("Connecting to server...")
    socket.connect("tcp://128.2.204.249:40001")  # bree
    time.sleep(1)

    request = json.dumps({
        "sensorVideoText": "tcp://128.2.212.138:40000",
        "sensorAudio": "tcp://128.2.212.138:40001",
        "sensorDOA": "tcp://128.2.212.138:40002",
        "sensorVAD": "tcp://128.2.212.138:40003"
    })

    payload = {
        'message': request,
        'originatingTime': datetime.datetime.utcnow().isoformat()
    }
    print(f"Sending request: {request}")
    socket.send_string(json.dumps(payload))
    # socket.send_string(json.dumps(request))

    reply = socket.recv()
    print(f"Received reply: {reply.decode()}")

def gui():
    # my_ip = find_my_ip()
    # share_my_ip_with_psi(my_ip)
    # send_IPs_to_PSI()
    
    # context = zmq.Context()
    # socket = context.socket(zmq.REQ)

    # print("Connecting to server...")
    # socket.connect("tcp://128.2.204.249:40001")   # bree
    # time.sleep(1)

    # # request = "tcp://72.95.139.140:40003"   # 140 W. Swissvale Ave.
    # request = json.dumps({"sensorVideoText":"tcp://128.2.212.138:40000", "sensorAudio": "tcp://128.2.212.138:40001", "sensorDOA": "tcp://128.2.212.138:40002", "sensorVAD": "tcp://128.2.212.138:40003"})   # erebor"
    # # request = "tcp://128.2.149.108:40003"
    # # request = "tcp://23.227.148.141:40003"

    # # Send the request
    # payload = {}
    # payload['message'] = request
    # payload['originatingTime'] = datetime.datetime.utcnow().isoformat()
    # print(f"Sending request: {request}")
    # socket.send_string(request)
    # print("Request sent.")
    # #  Get the reply
    # reply = socket.recv()
    # print(f"Received reply: {reply}")

    
    window = tk.Tk()
    window.title("Audio Recorder")
    window.attributes('-topmost', True)

    start_button = tk.Button(window, text="Start Recording", command=lambda: start_recording_thread('./output/', 1, start_button))
    start_button.pack()

    # Define the stop recording button action properly
    stop_button = tk.Button(window, text="Stop Recording", command=lambda: stop_recording_using_button(start_button))
    stop_button.pack()

    window.mainloop()

if __name__ == "__main__":
    gui()
