from time import sleep

from boosterCtrlLib.booster_quartiq import MqttServer

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

lab2_mqtt_broker_addr = "10.60.0.141"
lab2_mqtt_broker_port = 1882

# Here is the list of all used boosters macs
# e.g.:
# booster1_mac = "80-34-28-1b-7c-f2"
# booster2_mac = "80-34-28-1b-7c-f3"
# booster3_mac = "80-34-28-1b-7c-f4"
# etc.
booster1_mac = "80-34-28-1b-7c-f2"
booster2_mac = "80-34-28-1b-7c-f3"
booster3_mac = "80-34-28-1b-7c-f4"


def main():
    lab1 = MqttServer(broker_addr=lab1_mqtt_broker_addr, port=lab1_mqtt_broker_port)
    lab2 = MqttServer(broker_addr=lab2_mqtt_broker_addr, port=lab2_mqtt_broker_port)

    # Booster 1 and 2 conneted to broker in lab 1
    booster1 = lab1.open_resource(booster1_mac)
    booster2 = lab1.open_resource(booster2_mac)

    # Booster 3 connected to broker in lab 2
    booster3 = lab2.open_resource(booster3_mac)

    # Booster 1 operation
    # is_alive() allows to check if booster is connected to broker
    if not booster1.is_alive():
        print("Booster is not connected to broker or is turned off.")
        return

    # Turn off all channels
    for i in range(8):
        booster1.set_state(i, False)
    sleep(0.5)

    # Turn on all channels
    for i in range(8):
        booster1.set_state(i, True)
    sleep(0.5)

    # Save configuration
    for i in range(8):
        booster1.save_config(i)

    # Booster 2 operation
    # is_alive() allows to check if booster is connected to broker
    if not booster2.is_alive():
        print("Booster is not connected to broker or is turned off.")
        return

    # Turn off all channels
    for i in range(8):
        booster2.set_state(i, False)
    sleep(0.5)

    # Turn on all channels
    for i in range(8):
        booster2.set_state(i, True)
    sleep(0.5)

    # Save configuration
    for i in range(8):
        booster2.save_config(i)

    # Booster 3 operation
    # is_alive() allows to check if booster is connected to broker
    if not booster3.is_alive():
        print("Booster is not connected to broker or is turned off.")
        return

    # Turn off all channels
    for i in range(8):
        booster3.set_state(i, False)
    sleep(0.5)

    # Turn on all channels
    for i in range(8):
        booster3.set_state(i, True)
    sleep(0.5)

    # Save configuration
    for i in range(8):
        booster3.save_config(i)


if __name__ == '__main__':
    main()