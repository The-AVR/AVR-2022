# Importing the necessary libraries for the MQTT communication, logging, and threading
from bell.avr.mqtt.client import MQTTModule  # MQTTModule class from the MQTT client library
from bell.avr.mqtt.payloads import AvrFcmStatusPayload  # Importing a specific payload class for message handling

import time
from threading import Thread


# Defining a new class called Sandbox which inherits from MQTTModule
class Sandbox(MQTTModule):
    def __init__(self) -> None:  # Defining the class constructor
        super().__init__()  # Invoking the parent class (MQTTModule) constructor
        # Subscribe to MQTT topics and give them a call back function here
        self.topic_map = {
            "avr/fcm/status": self.handle_status_message,
            "avr/vio/confidence": self.handle_vio_message,
        }

        # Defining a variable to keep track of the vehicle's armed status
        self.is_armed: bool = False
        self.confidence = -1  # Defining a variable for confidence value

        # Defining the colors as lists of RGB values
        self.color_green = [0, 0, 255, 0]
        self.color_red = [0, 255, 0, 0]
        self.color_yellow = [0, 252, 186, 3]

    # Function to handle the status message. It updates the system's armed status
    def handle_status_message(self, payload: AvrFcmStatusPayload) -> None:
        armed = payload["armed"]  # Extracting the 'armed' status from the message payload
        self.is_armed = armed  # Updating the system's armed status

    # Function to handle the vio message. It updates the confidence value
    def handle_vio_message(self, payload: dict) -> None:
        confidence = payload["tracker"]  # Extracting the 'tracker' value from the message payload
        if confidence >= 0 and confidence <= 100:  # Validating the confidence value
            self.confidence = confidence  # Updating the confidence value

    # The main loop where the system checks its status and updates the color accordingly
    def loop(self):
        while True:  # Runs in an Infinite loop
            # set the color according to our conditions
            color = self.color_red
            if self.is_armed:
                color = self.color_green
                if self.confidence < 75:  # If confidence is less than 75
                    color = self.color_yellow  # Change color to yellow

            # Sends a message with the new color
            # this is where you can send your waypoint messages
            # see the FCM for message definition
            self.send_message("avr/pcm/set_base_color", {"wrgb": color})
            time.sleep(1)  # Wait for 1 second before the next iteration


# This is the entry point of the program
if __name__ == "__main__":
    # Initialize Sandbox class
    box = Sandbox()

    # Create a new thread for running the loop function independently of the main program
    loop_thread = Thread(target=box.loop)
    loop_thread.setDaemon(True)  # Setting the thread as a Daemon so it will end when the main program ends
    loop_thread.start()  # Starting the new thread

    box.run()  # Running the main MQTT client