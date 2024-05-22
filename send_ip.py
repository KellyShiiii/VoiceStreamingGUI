import stomp
import time
import json
from datetime import datetime

class ActiveMQSender(stomp.ConnectionListener):
    def __init__(self, server, port):
        self.conn = stomp.Connection(host_and_ports=[(server, port)])
        self.conn.set_listener('', self)
        self.conn.start()
        self.conn.connect(wait=True)

    def send_to_psi(self, data):
        try:
            message = json.dumps(data)
            self.conn.send(body=message, destination='/queue/PSIQueue')
            print(f"Sent: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")

    def on_error(self, frame):
        print('Received an error:', frame.body)

    def on_message(self, frame):
        print('Received a message:', frame.body)

    def disconnect(self):
        self.conn.disconnect()

def send_IPs_to_PSI():
    sender = ActiveMQSender('128.2.204.249', 61613)  # Default STOMP port is 61613
    
    data = {
        "sensorVideoText": "tcp://128.2.212.138:40000",
        "sensorAudio": "tcp://128.2.212.138:40001",
        "sensorDOA": "tcp://128.2.212.138:40002",
        "sensorVAD": "tcp://128.2.212.138:40003",
        "message": "sensor information",
        "originatingTime": datetime.utcnow().isoformat()
    }

    print("Connecting to server...")
    time.sleep(1)  # Simulate some delay

    print(f"Sending data to PSI...")
    sender.send_to_psi(data)

    # Allow some time to process the message
    time.sleep(2)

    sender.disconnect()

if __name__ == "__main__":
    send_IPs_to_PSI()
