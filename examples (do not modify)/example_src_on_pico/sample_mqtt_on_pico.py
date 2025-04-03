"""
Example showing a Pico, running CircuitPython,
communicating with another device through MQTT.

Author:  David Mutchler, Rose-Hulman Institute of Technology,
         based on examples from the internet.
"""

import random  # Import for simulating sending sensor data
import mqtt_helper_pico  # NEED THIS!


# -----------------------------------------------------------------------------
# NEED THE FOLLOWING to initialize the Pico/MQTT interaction.
# -----------------------------------------------------------------------------
class MyHook:
    def __init__(self):
        pass

    def on_message(self, message, client):
        react_to_message(message, client)


mqtt_client = mqtt_helper_pico.MyMqttClient(MyHook())

# -----------------------------------------------------------------------------
# YOUR CODE STARTS HERE.  The following is just an EXAMPLE that:
#    1. Repeatedly SENDS random messages (to simulate sensor data).
#    2. Blinks the LED light twice rapidly when a message is RECEIVED.
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------
import board
import digitalio
import time

# -----------------------------------------------------------------------------
# GLOBAL VARIABLES:
# -----------------------------------------------------------------------------
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS:
#   NEED something like this EXAMPLE showing how to
#   RECEIVE a message from the PC and respond to it.
# -----------------------------------------------------------------------------
def react_to_message(message, client):
    try:
        blink_rapidly(int(message))
    except Exception as e:
        print("Could not react to message", message, "because:")
        print(e)
        blink_rapidly()


def blink_rapidly(number_of_times_to_blink=4):
    for k in range(number_of_times_to_blink):
        led.value = True
        time.sleep(0.1)
        led.value = False
        time.sleep(0.1)


# -----------------------------------------------------------------------------
# MAIN LOOP:
# -----------------------------------------------------------------------------
while True:
    # -------------------------------------------------------------------------
    # NEED THIS! Poll for about 1 second to see if any messages have arrived
    # -------------------------------------------------------------------------
    mqtt_client.loop(timeout=1)

    # -------------------------------------------------------------------------
    # Send random numbers (simulating sending sensor data):
    # -------------------------------------------------------------------------
    simulated_sensor_data = random.randint(1, 100)
    message_to_send = str(simulated_sensor_data)

    # -------------------------------------------------------------------------
    # NEED something like THIS: EXAMPLE showing how to SEND a message to the PC.
    # -------------------------------------------------------------------------
    print("Sending message:", message_to_send)
    mqtt_client.publish(mqtt_helper_pico.DEVICE_TO_PC_TOPIC, message_to_send)

    # -------------------------------------------------------------------------
    # Sleep as needed to avoid inundating the main loop and/or message-passing.
    # -------------------------------------------------------------------------
    time.sleep(5)
