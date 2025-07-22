from time import sleep

from boosterCtrlLib.booster_quartiq import MqttServer, BoosterQuartiq

# Here is the list of all used brokers
# e.g.:
# lab1_mqtt_broker_addr = "10.60.0.140"
# lab1_mqtt_broker_port = 1883
# lab2_mqtt_broker_addr = "10.60.0.141"
# lab2_mqtt_broker_port = 1882
# lab3_mqtt_broker_addr = "10.60.0.142"
# lab3_mqtt_broker_port = 1881
# etc.
lab1_mqtt_broker_addr = "10.60.0.140"
lab1_mqtt_broker_port = 1883

# Here is the list of all used boosters macs
# e.g.:
# booster1_mac = "80-34-28-1b-7c-f2"
# booster2_mac = "80-34-28-1b-7c-f3"
# booster3_mac = "80-34-28-1b-7c-f4"
# etc.
booster1_mac = "80-34-28-1b-7c-f2"


def print_telemetry(booster: BoosterQuartiq, channel: int):
    telemetry = booster.get_telemetry(channel)
    if telemetry is None:
        print(f"Telemetry for channel {channel} is not available.")
        return
    telemetry_string = (
        f"Telemetry for channel {channel}\n"
        f"reflected overdrive: {telemetry['reflected_overdrive']}\n"
        f"output overdrive: {telemetry['output_overdrive']}\n"
        f"alert: {telemetry['alert']}\n"
        f"temperature: {telemetry['temperature']}\n"
        f"p28v_current: {telemetry['p28v_current']}\n"
        f"p5v_current: {telemetry['p5v_current']}\n"
        f"p5v_voltage: {telemetry['p5v_voltage']}\n"
        f"input power: {telemetry['input_power']}\n"
        f"reflected power: {telemetry['reflected_power']}\n"
        f"output power: {telemetry['output_power']}\n"
        f"state: {telemetry['state']}\n"
        f"-----------------------------------------------"
    )
    print(telemetry_string)


def main():
    lab1 = MqttServer(broker_addr=lab1_mqtt_broker_addr, port=lab1_mqtt_broker_port)

    booster1 = lab1.open_resource(booster1_mac)

    if not booster1.is_alive():
        print("Booster is not connected to broker or is turned off.")
        return
    channel_telemetry = 0

    while True:
        print_telemetry(booster1, channel_telemetry)
        sleep(booster1.get_telemetry_period())


if __name__ == '__main__':
    main()