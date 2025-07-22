import time
import json
import logging
import threading
import uuid
import re

# MQTT client library for Quartiq devices
# python -m pip install git+https://github.com/quartiq/miniconf#subdirectory=py/miniconf-mqtt

import paho.mqtt
import miniconf.sync as miniconf
from miniconf.common import LOGGER, MQTTv5
from paho.mqtt.properties import Properties, PacketTypes

logging.basicConfig(level=logging.ERROR)


class MiniconfSync(miniconf.Miniconf):
    def __init__(self, client: miniconf.Client, prefix: str):
        """
            Synchronous miniconf class inhereting after Main Miniconf.
            :param client: MQTT Client handle.
            :param prefix: prefix to booster data in broker.
        """
        super().__init__(client, prefix)

    def save_config(self, path, timeout=None, **kwargs):
        """
        Initialize the MQTT server connection.
        :param path: mqtt topic suffix.
        """
        props = Properties(PacketTypes.PUBLISH)
        event = threading.Event()
        ret = []
        cd = uuid.uuid1().bytes
        props.ResponseTopic = self.response_topic
        props.CorrelationData = cd
        assert cd not in self._inflight
        self._inflight[cd] = event, ret

        topic = f"{self.prefix}{path}"
        LOGGER.debug("Publishing %s: %s, [%s]", topic, kwargs.get("payload"), props)
        _pub = self.client.publish(topic, properties=props, **kwargs)

        event.wait(timeout)
        return ret

class PwrType:
    INPUT = "input_power"
    OUTPUT = "output_power"
    REFLECTED = "reflected_power"


class MqttServer:
    def __init__(self, broker_addr='localhost', port=1883):
        """
        Initialize the MQTT server connection.
        :param broker_addr: IP address of the MQTT server.
        :param port: Port number of the MQTT server.
        """
        self.broker_addr = broker_addr
        self.port = port
        self.client = None
        self.miniconf = None

    def open_resource(self, booster_id: str):
        """
        Open a connection to the booster device.
        :param booster_id: MAC address of the booster device.
        :return: BoosterDevice
        """
        self.client = miniconf.Client(paho.mqtt.enums.CallbackAPIVersion.VERSION2, protocol=MQTTv5)
        self.client.connect(self.broker_addr, self.port, keepalive=60)
        self.client.loop_start()
        prefix = f"dt/sinara/booster/{booster_id}"
        self.miniconf = MiniconfSync(self.client, prefix)
        print(f"Connecting to booster at {booster_id} via MQTT server {self.broker_addr}:{self.port}")
        return BoosterQuartiq(booster_id, self.miniconf)


class BoosterQuartiq:
    def __init__(self, mac: str, miniconf: MiniconfSync):
        """ Constructor for BoosterQuartiq.

        Args:
            mac (str): MAC address of the booster.
            miniconf (miniconf.Miniconf): Miniconf instance for MQTT communication.
        """
        self.booster_id = mac
        self.miniconf = miniconf

    def get_telemetry_data(self, topic_suffix: str, timeout: float = 3.0) -> str:
        """
        Subscribes synchronously to a telemetry topic and waits for a single message.

        Args:
            topic_suffix (str): e.g. "/ch0"
            timeout (float): Time in seconds to wait for a response

        Returns:
            str: Decoded payload of the MQTT message
        """
        topic = f"{self.miniconf.prefix}{topic_suffix}"
        event = threading.Event()
        result = {}

        client = self.miniconf.client

        def on_message(_client, _userdata, message):
            result["payload"] = message.payload.decode("utf-8")
            event.set()

        client.message_callback_add(topic, on_message)
        client.subscribe(topic)

        try:
            if not event.wait(timeout):
                raise TimeoutError(f"No telemetry received on {topic} in {timeout} seconds")
            return result["payload"]
        finally:
            client.message_callback_remove(topic)
            client.unsubscribe(topic)

    def is_alive(self, timeout=15):
        """Method for checking if Booster is correctly connected to MQTT Broker "
        Args: None
        :return: Bool
        """
        mqtt_topic = f"{self.miniconf.prefix}/alive"
        for _ in range(timeout):
            msg = self.miniconf.client.subscribe(mqtt_topic)
            if msg:
                return True
            time.sleep(1)
        return False


    def get_slope(self, channel: int, pwr_type: str):
        """ Get the calibration slope for a given channel and power type.

        Args:
            channel (int): channel number (0-7).
            pwr_type (PwrType): Power type (INPUT, OUTPUT, REFLECTED).
        Returns:
            float: The slope value for the specified channel and power type.
        """
        path = f"/channel/{channel}/{pwr_type}_transform"
        slope = self.miniconf.get(path)
        return slope["slope"]

    def get_offset(self, channel: int, pwr_type: str):
        """ Get the calibration offset for a given channel and power type.

        Args:
            channel (int): channel number (0-7).
            pwr_type (PwrType): Power type (INPUT, OUTPUT, REFLECTED).

        Returns:
            float: The offset value for the specified channel and power type.
        """
        path = f"/channel/{channel}/{pwr_type}_transform"
        offset = self.miniconf.get(path)
        return offset["offset"]

    def get_telemetry_period(self):
        """ Get the telemetry period set on booster.

        Returns:
            float: Telemetry period in seconds.
        """
        path = f"/telemetry_period"
        period = self.miniconf.get(path)
        return period

    def set_calibration(self, channel: int, pwr_type: str, slope: float, offset: float):
        """ Set the calibration parameters for a given channel and power type.

        Args:
            channel (int): channel number (0-7).
            pwr_type (PwrType): Power type (INPUT, OUTPUT, REFLECTED).
            slope (float): The slope value to set for the specified channel and power type.
            offset (float): The offset value to set for the specified channel and power type.
        :return: None
        """
        payload = {'slope': slope, 'offset': offset}
        self.miniconf.set(f"/channel/{channel}/{pwr_type}_transform", payload)

    def set_telemetry_period(self, period_sec: int):
        """ Set the telemetry period for the booster.

        Args:
            period_sec (int): The period in seconds for telemetry updates.
        """
        path = f"/telemetry_period"
        self.miniconf.set(path, period_sec)

    def set_fan_speed(self, fan_speed: float):
        """ Set the fan speed for the booster.
        Args:
            fan_speed (float): The desired fan speed value (0.0 to 1.0).
        :return: None
        """
        path = f"/fan_speed"
        self.miniconf.set(path, fan_speed)

    def set_state(self, channel: int, state: bool):
        """ Set the state of a specific channel.

        Args:
            channel (int): channel number (0-7). 
            state (bool): True to enable the channel, False to disable it.
        :return: None
        """
        path = f"/channel/{channel}/state"
        value = "Enabled" if state else "Off"
        self.miniconf.set(path, value)

    def set_output_interlock_th(self, channel: int, int_val: float):
        """ Set the output interlock threshold for a specific channel.

        Args:
            channel (int): channel number (0-7).
            int_val (float): The interlock threshold value to set for the specified channel.
        :return: None
        """
        path = f"/channel/{channel}/output_interlock_threshold"
        self.miniconf.set(path, int_val)

    def set_bias_voltage(self, channel: int, bias_val: float):
        """ Set the bias voltage for a specific channel.

        Args:
            channel (int): channel number (0-7).
            bias_val (float): The bias voltage value to set for the specified channel.
        :return: None
        """
        path = f"/channel/{channel}/bias_voltage"
        self.miniconf.set(path, bias_val)

    def get_telemetry(self, channel: int):
        """ Get the telemetry data for a specific channel.

        Args:
            channel (int): channel number (0-7).
        """
        path = f"/telemetry/ch{channel}"
        return json.loads(self.get_telemetry_data(path))

    def save_config(self, channel: int):
        """ Save the configuration of a specific channel to the BOOSTER.

        Args:
            channel (int): channel number (0-7).
        :return: None
        """
        path = f"/command/save"
        channel_string = ["Zero", 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven']
        message = json.dumps({"channel": channel_string[channel]})
        return self.miniconf.save_config(path, payload=message)