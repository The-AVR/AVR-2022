# Here we import our own MQTT library which takes care of a lot of boilerplate
# code related to connecting to the MQTT server and sending/receiving messages.
# It also helps us make sure that our code is sending the proper payload on a topic
# and is receiving the proper payload as well.
from bell.vrc.mqtt.client import MQTTModule
from bell.vrc.mqtt.payloads import VrcFcmVelocityPayload

# This imports the third-party Loguru library which helps make logging way easier
# and more useful.
# https://loguru.readthedocs.io/en/stable/
from loguru import logger


# This creates a new class that will contain multiple functions
# which are known as "methods". This inherits from the MQTTModule class
# that we imported from our custom MQTT library.
class Sandbox(MQTTModule):
    # The "__init__" method of any class is special in Python. It's what runs when
    # you create a class like `sandbox = Sandbox()`. In here, we usually put
    # first-time initialization and setup code. The "self" argument is a magic
    # argument that must be the first argument in any class method. This allows the code
    # inside the method to access class information.
    def __init__(self) -> None:
        # Here, we're creating a dictionary of MQTT topic names to method handles.
        # A dictionary is a data structure that allows use to
        # obtain values based on keys. Think of a dictionary of state names as keys
        # and their capitals as values. By using the state name as a key, you can easily
        # find the associated capital. However, this does not work in reverse. So here,
        # we're creating a dictionary of MQTT topics, and the methods we want to run
        # whenever a message arrives on that topic.
        self.topic_map = {"vrc/fcm/velocity": self.show_velocity}

    # Here's an example of a custom message handler here.
    # This is what executes whenever a message is received on the "vrc/fcm/velocity"
    # topic. The content of the message is passed to the `payload` argument.
    # The `VrcFcmVelocityMessage` class here is beyond the scope of VRC.
    def show_velocity(self, payload: VrcFcmVelocityPayload) -> None:
        vx = payload["vX"]
        vy = payload["vY"]
        vz = payload["vZ"]
        v_ms = (vx, vy, vz)

        # Use methods like `debug`, `info`, `success`, `warning`, `error`, and
        # `critical` to log data that you can see while your code runs.

        # This is what is known as a "f-string". This allows you to easily inject
        # variables into a string without needing to combine lots of strings together.
        # https://realpython.com/python-f-strings/#f-strings-a-new-and-improved-way-to-format-strings-in-python
        logger.debug(f"Velocity information: {v_ms} m/s")

    # Here is an example on how to publish a message to an MQTT topic to
    # perform an action
    def open_servo(self) -> None:
        # It's super easy, use the `self.send_message` method with the first argument
        # as the topic, and the second argument as the payload.
        # Pro-tip, if you set `python.analysis.typeCheckingMode` to `basic` in you
        # VS Code preferences, you'll get a red underline if your payload doesn't
        # match the expected format for the topic.
        self.send_message(
            "vrc/pcm/set_servo_open_close",
            {"servo": 0, "action": "open"},
        )


if __name__ == "__main__":
    # This is what actually initializes the Sandbox class, and executes it.
    # This is nested under the above condition, as otherwise, if this file
    # were imported by another file, these lines would execute, as the interpreter
    # reads and executes the file top-down. However, whenever a file is called directly
    # with `python file.py`, the magic `__name__` variable is set to "__main__".
    # Thus, this code will only execute if the file is called directly.
    box = Sandbox()
    # The `run` method is defined by the inherited `MQTTModule` class and is a
    # convience function to start processing incoming MQTT messages infinitely.
    box.run()
