#  Library for Booster Control via MQTT

This project allows you to control and monitor Quartiq Booster devices using the MQTT protocol. It enables channel control, telemetry reading, and configuration saving across multiple brokers.

---

## Project Structure

```
boosterCtrlLib/
│
├── booster_quartiq.py      # Core MQTT/Miniconf interface for booster control
│
examples/
├── demo_channel_control.py    # Example: control a single booster
├── demo_telemetry.py          # Example: read telemetry from given channel
├── demo_multiple_boosters.py  # Example: control multiple boosters connected to one broker
├── demo_multiple_brokers.py   # Example: control multiple boosters connected to different brokers
│
Windows/                              
├── dfu-util/                   # Dfu-util pack needed for firmware update using Windows OS
Linux/
├── mosquitto/                  # files needed to setup mosquitto using Linux OS
requirements.txt            # Python dependencies
README.md                   # This file
main.py                     # Main file with one channel control and telemetry reading
```

---

##  Requirements

>  Mosquitto broker has to be setup and running in order to use this software. 

###  Python 3.8+

It is recommended to use python version 3.8+.

###  Install Dependencies

Install Python packages:

   ```bash
   pip3 install -r requirements.txt
   ```

---

>  `miniconf-mqtt` is installed directly from Quartiq's GitHub repository.

---
##  Running main 

```bash
python3 main.py
```
---
##  Running Demos

Each script under the `examples/` directory demonstrates different features:

###  Control a Single Booster

```bash
python3 examples/demo_channel_control.py
```

###  Read telemetry from single Booster

```bash
python3 examples/demo_telemetry.py
```

###  Control multiple Booster in one Lab

```bash
python3 examples/demo_multiple_boosters.py  
```

###  Control multiple Boosters in multiple Labs

```bash
python3 examples/demo_multiple_brokers.py
```

---

##  Notes

* Broker IP addresses and booster MAC addresses are hardcoded in each script.
* To add or change boosters/brokers, edit the appropriate section in `demo_*.py` files.

---


