import requests
import json
import time
import random

# Configuration
API_KEY = '98308c99d4f683bf560b530c92c545b5'
LAT = 51.0414775  # Latitude for Ghent
LON = 3.7598537   # Longitude for Ghent
UPDATE_INTERVAL = 48 * 24 * 3600  # Update every 2 days

class Battery:
    def __init__(self, voltage, capacity, soc=100):
        self.voltage = voltage
        self.capacity = capacity
        self.current_capacity = soc  * capacity / 100

    def charge(self, power):
        self.current_capacity += power
        return self.current_capacity

    def discharge(self, power):
        self.current_capacity -= power
        return self.current_capacity

    def get_soc(self):
        return self.current_capacity / self.capacity * 100

class Inverter:
    def __init__(self, api_key, lat, lon, update_interval):
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.update_interval = update_interval
        self.mode = 'self_use'  # Default mode
        self.battery = Battery(100, 3000, 50)  # 48V, 3000Wh

    def fetch_weather(self):
        with open('test_weather.json', 'r') as file:
            return json.load(file)
        # url = f'https://api.openweathermap.org/data/3.0/onecall?lat={self.lat}&lon={self.lon}&appid={self.api_key}'
        # response = requests.get(url)
        # return response.json()

    def uvi_to_power(self, uvi):
        power_output = min(max(uvi / 10 * 100, 0), 100) * 300
        return power_output

    def calculate_solar_panel(self, power_output):
        solar_panel_voltage = 40
        solar_panel_current = power_output / solar_panel_voltage
        return solar_panel_voltage, solar_panel_current

    def calculate_inverter(self, power_output):
        inverter_power = power_output
        inverter_voltage = 230
        inverter_current = inverter_power / inverter_voltage
        return inverter_power, inverter_voltage, inverter_current

    def simulate_load(self):
        # Simulate a load that changes every 10 seconds
        return random.randint(100, 1000)  # Load in watts

    def run(self):
        while True:
            weather_data = self.fetch_weather()
            for i in range(0, 48):
                while weather_data['hourly'][i]['dt'] < time.time() and weather_data['hourly'][i + 1]['dt'] > time.time():
                    uvi = weather_data['hourly'][i]['uvi']
                    power_output = self.uvi_to_power(uvi)
                    
                    solar_panel_voltage, solar_panel_current = self.calculate_solar_panel(power_output)
                    inverter_power, inverter_voltage, inverter_current = self.calculate_inverter(power_output)
                    
                    load = self.simulate_load()
                    
                    if self.mode == 'self_use':
                        print("Mode: Self Use")
                        # Use generated power for self-consumption
                        if inverter_power >= load:
                            battery_power = (inverter_power - load) * 0.8
                            self.battery.charge(battery_power)
                            inverter_power = load  # Remaining power goes to the load
                        else:
                            battery_power = 0
                            #load = inverter_power  # All power goes to the load
                    elif self.mode == 'backup':
                        print("Mode: Backup")
                        # Store power for backup purposes
                        battery_power = power_output * 0.8
                        self.battery.charge(battery_power)
                        inverter_power = 0  # No power output to the grid
                    elif self.mode == 'force_charge':
                        print("Mode: Force Charge")
                        # Force charging the battery
                        battery_power = power_output * 0.8
                        self.battery.charge(battery_power)
                        inverter_power = 0  # No power output to the grid
                    elif self.mode == 'force_discharge':
                        print("Mode: Force Discharge")
                        # Force discharging the battery
                        battery_power = -inverter_power * 0.8
                        self.battery.discharge(battery_power)
                        inverter_power = power_output  # Power output to the grid
                    
                    battery_soc = self.battery.get_soc()
                    
                    print(f'UVI: {uvi}, Inverter Output: {inverter_power}W')
                    print(f'Solar Panel - Voltage: {solar_panel_voltage}V, Current: {solar_panel_current:.2f}A')
                    print(f'Inverter - Power: {inverter_power}W, Voltage: {inverter_voltage}V, Current: {inverter_current:.2f}A')
                    print(f'Battery - Power: {battery_power}W, Voltage: {self.battery.voltage}V, Current: {battery_power / self.battery.voltage:.2f}A, SoC: {battery_soc:.2f}%')
                    print(f'Load: {load}W')
                    
                    time.sleep(10)  # Simulate load change every 10 seconds
            time.sleep(self.update_interval)

if __name__ == '__main__':
    inverter = Inverter(API_KEY, LAT, LON, UPDATE_INTERVAL)
    inverter.run()