"""
Code for a Pico to communicate with another device through MQTT.
Use verbatim except where TODO's indicate.

Author:  David Mutchler, Rose-Hulman Institute of Technology,
         based on examples from the internet.
"""

# -----------------------------------------------------------------------------
# You need the following Adafruit libraries in the  lib  folder on the Pico:
#    adafruit_minimqtt
#    adafruit_connection_manager.mpy
#    adafruit_ticks.mpy
#
# You also need a  secrets.py  file with the required information.
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# These imports are for the WIFI and MQTT communication:
# -----------------------------------------------------------------------------
import ssl
import sys

import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# -----------------------------------------------------------------------------
# MQTT Topics to publish/subscribe from Pico to other devices via the broker.
# -----------------------------------------------------------------------------
UNIQUE_ID = "DavidMutchler1019"  # TODO: Use something no one else will use
PC_TO_DEVICE_TOPIC = UNIQUE_ID + "/pc_to_device"
DEVICE_TO_PC_TOPIC = UNIQUE_ID + "/device_to_pc"

# -----------------------------------------------------------------------------
# Load the WiFi and broker credentials from the file: secrets.py
# -----------------------------------------------------------------------------
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# -----------------------------------------------------------------------------
# Connect to the configured WiFi network
# -----------------------------------------------------------------------------
print(f"Attempting to connect to WiFi: {secrets['ssid']} ...")
try:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
except Exception as e:
    print("  Could NOT connect to WiFi. Error message was:")
    print(e)
    sys.exit(1)

print(f"  CONNECTED to wifi {secrets['ssid']}")

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)


# -----------------------------------------------------------------------------
# Set up a MiniMQTT Client
# -----------------------------------------------------------------------------
HOOK_TO_PICO_CODE = None  # Set when the Mqtt client is constructed (below).


class MyMqttClient(MQTT.MQTT):
    def __init__(self, hook_to_pico_code):
        super().__init__(
            broker=secrets["broker"],
            port=secrets["port"],
            username=secrets["mqtt_username"],
            password=secrets["mqtt_key"],
            socket_pool=pool,
            ssl_context=ssl.create_default_context(),
        )
        global HOOK_TO_PICO_CODE
        HOOK_TO_PICO_CODE = hook_to_pico_code

        self.on_connect = on_connect
        self.on_subscribe = on_subscribe
        self.on_message = on_message
        self.on_disconnect = on_disconnect
        self.on_unsubscribe = on_unsubscribe
        # self.on_publish = on_publish

        # ---------------------------------------------------------------------
        # TODO: Put your instance variables here as needed, all set to None
        # ---------------------------------------------------------------------
        self.number_of_messages_received = None  # Set later

        print(f"Attempting to connect to {secrets['broker']}")
        try:
            self.connect()
            self.subscribe(PC_TO_DEVICE_TOPIC)
        except Exception as e:
            print("  MQTT connect FAILED: ", e)


# -----------------------------------------------------------------------------
# Define callback methods and assign them to the MQTT events
# -----------------------------------------------------------------------------
def on_connect(client, userdata, flags, reason_code):
    if reason_code == 0:
        print(f"  CONNECTED to MQTT broker {client.broker}")
    else:
        print(f"  Failed to connect to broker, reason code {reason_code}")


def on_disconnect(mqtt_client, userdata, rc):
    print("Disconnected from MQTT Broker!")


def on_subscribe(mqtt_client, userdata, topic, granted_qos):
    print("  SUBSCRIBED to {0} with QOS level {1}".format(topic, granted_qos))


def on_unsubscribe(mqtt_client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def on_publish(mqtt_client, userdata, topic, pid):
    print("Published to {0} with PID {1}".format(topic, pid))


def on_message(mqtt_client, userdata, message):
    # -------------------------------------------------------------------------
    # TODO: Modify as needed for your Pico behavior.
    # -------------------------------------------------------------------------
    print("Received a message:", message)
    HOOK_TO_PICO_CODE.on_message(message, mqtt_client)


# -----------------------------------------------------------------------------
# TODO: CALL (do NOT modify) as needed for your GUI
# -----------------------------------------------------------------------------
def send_via_mqtt(message, mqtt_client):
    """Publish (send to other device) the given string."""
    print("Sending message:", message)  # For debugging, as needed
    mqtt_client.publish(DEVICE_TO_PC_TOPIC, message)
