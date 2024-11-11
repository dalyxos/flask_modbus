import threading
import time
import requests
from enum import Enum

class InverterMode(Enum):
    SELF_USE = "self_use"
    BACKUP = "backup"
    STOP_CHARGE_DISCHARGE = "stop_charge_discharge"
    FORCE_CHARGE = "force_charge"
    FORCE_DISCHARGE = "force_discharge"

class Inverter:
    def __init__(self, model, capacity):
        self.model = model
        self.voltage = 230
        self.mode = InverterMode.SELF_USE
        self.pv_panels = SolarPanels()
        self.battery = Battery()
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.start()

    def run(self):
        self.running = True

    def get_status(self):
        # ...existing code...
        pass

    def start(self):
        # ...existing code...
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def set_mode(self, mode):
        self.mode = mode


class SolarPanels:
    def __init__(self, panel_count=10, efficiency=0.18):  # Setting a typical default panel count of 10 and efficiency of 18%
        self.panel_count = panel_count
        self.efficiency = efficiency
        self.total_area = 1.6 * self.panel_count  # Assuming each panel has an area of 1.6 square meters
        self.orientation = 0
        self.power = 0
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.start()

    def run(self):
        self.delay = 900  # 15 minutes
        self.running = True
        while self.running:
            self.update_power()
            time.sleep(self.delay)  # 15 minutes

    def update_power(self):
        response = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": 51.05,
            "longitude": 3.7167,
            "current": "solar_radiation",
            "timezone": "auto"
        })
        data = response.json()
        solar_radiation = data["current"]["solar_radiation"]  # Example, adjust as needed
        self.delay = data["current"]["time"] + data["current"]["interval"] - time.time()
        self.power = solar_radiation * self.efficiency * self.total_area

    def get_power_output(self):
        return self.power

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

class BatteryType(Enum):
    LITHIUM_ION = "lithium_ion"
    LEAD_ACID = "lead_acid"

class Battery:
    def __init__(self, capacity=3000, soc = 0):
        self.type = BatteryType.LITHIUM_ION
        self.max_capacity = capacity
        self.current_capacity = soc * capacity
        self.voltage = 100
        self.current = 0
        self.max_charge_current = 30
        self.max_discharge_current = 30
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.start()

    def run(self):
        self.running = True
        while self.running:
            self.current_capacity += self.current * self.voltage * 5 / 3600
            time.sleep(5)

    def charge(self, current):
        self.current = current

    def discharge(self, current):
        self.current = -current

    def get_charge_level(self):
        return self.current_capacity * 100 / self.max_capacity

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
