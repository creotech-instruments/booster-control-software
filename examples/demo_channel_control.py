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

# Here is the list of all used boosters macs
# e.g.:
# booster1_mac = "80-34-28-1b-7c-f2"
# booster2_mac = "80-34-28-1b-7c-f3"
# booster3_mac = "80-34-28-1b-7c-f4"
# etc.
booster1_mac = "80-34-28-1b-7c-f2"


def main():
    lab1 = MqttServer(broker_addr=lab1_mqtt_broker_addr, port=lab1_mqtt_broker_port)

    booster1 = lab1.open_resource(booster1_mac)

    # is_alive() allows to check if booster is connected to broker
    if not booster1.is_alive():
        print("Booster is not connected to broker or is turned off.")
        return

    # Turn on even channels and turn off odd channels
    for i in range(8):
        booster1.set_state(i, i % 2 == 0)
    sleep(0.5)

    # Turn off all channels
    for i in range(8):
        booster1.set_state(i, False)
    sleep(0.5)

    # Turn on all channels
    for i in range(8):
        booster1.set_state(i, True)
    sleep(0.5)

    # Turn off channels 0, 1, 2, 3
    for i in range(4):
        booster1.set_state(i, False)

    # Save configuration
    for i in range(8):
        booster1.save_config(i)

    print("Channels 0,1,2,3 deactivated and configuration saved.")

        
if __name__ == '__main__':
    main()