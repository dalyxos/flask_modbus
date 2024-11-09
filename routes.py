# routes.py
from flask import Flask, request, jsonify, render_template
from modbus_server import create_modbus_server, stop_modbus_server, get_modbus_server_context
import json
import threading
import time
import random
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

app = Flask(__name__)

# Global dictionary to store actions
actions = {}


# Load server configuration from JSON file
def load_server_config():
    try:
        with open('/app/data/servers.json') as f:
            return json.load(f)
    except FileNotFoundError:
        with open('./config/servers.json') as f:
            return json.load(f)


# Function to apply actions periodically
def apply_actions():
    while True:
        for server_id, params in actions.items():
            context = get_modbus_server_context(server_id)
            if context:
                for param_name, action in params.items():
                    for param in server_config['servers'][0]['parameters']:  # Assuming single server type for simplicity
                        if param['name'] == param_name:
                            address = param['address']
                            function_code = param['function_code']
                            current_value = context[0].getValues(function_code, address, count=1)[0]
                            if action == 'random':
                                new_value = random.randint(0, 100)
                            elif action == 'increment':
                                new_value = current_value + 1
                            elif action == 'reset':
                                new_value = 0
                            else:
                                new_value = current_value
                            context[0].setValues(function_code, address, [new_value])
        time.sleep(1)  # Apply actions every 5 seconds


# Start the action application thread
action_thread = threading.Thread(target=apply_actions)
action_thread.daemon = True
action_thread.start()


# REST API to create a new Modbus server
@app.route('/api/create_server', methods=['POST'])
def api_create_server():
    data = request.json
    server_id = data['server_id']
    address = data['address']
    port = data['port']
    parameters = {}
    for server_cfg in server_config['servers']:
        if server_id == f"{server_cfg['type']}_{server_cfg['port']}":
            parameters = server_cfg['parameters']
    create_modbus_server(server_id, address, port, parameters)
    return jsonify({'status': 'success', 'server_id': server_id})


# REST API to stop a Modbus server
@app.route('/api/stop_server/<server_id>', methods=['POST'])
def api_stop_server(server_id):
    if stop_modbus_server(server_id):
        return jsonify({'status': 'success', 'server_id': server_id})
    else:
        return jsonify({'status': 'error', 'message': 'Server not found'}), 404


# REST API to get register values for a Modbus server
@app.route('/api/get_registers/<server_id>', methods=['GET'])
def api_get_registers(server_id):
    context = get_modbus_server_context(server_id)
    if context:
        parameters = request.args.get('parameters')
        parameters = json.loads(parameters)
        values = {}
        for param in parameters:
            fc = param['function_code']
            address = param['address']
            values[param['name']] = context[0].getValues(fc, address, count=1)[0]
        return jsonify(values)
    else:
        return jsonify({'status': 'error', 'message': 'Server not found'}), 404


# REST API to set a single register value for a Modbus server
@app.route('/api/set_register/<server_id>', methods=['POST'])
def api_set_register(server_id):
    context = get_modbus_server_context(server_id)
    if context:
        data = request.json
        address = data['address']
        function_code = data['function_code']
        value = data['value']
        context[0].setValues(function_code, address, [value])
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Server not found'}), 404


# REST API to set an action for a parameter
@app.route('/api/set_action/<server_id>', methods=['POST'])
def api_set_action(server_id):
    data = request.json
    param_name = data['param_name']
    action = data['action']
    if server_id not in actions:
        actions[server_id] = {}
    actions[server_id][param_name] = action
    return jsonify({'status': 'success'})

@app.route('/radiation')
def radiation():
    return render_template('radiation.html')

@app.route('/api/direct_radiation')
def direct_radiation():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 51.05,
        "longitude": 3.7167,
        "hourly": "direct_radiation",
        "timezone": "auto"
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    hourly_direct_radiation = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["direct_radiation"] = hourly_direct_radiation
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    data = {
        'dates': hourly_dataframe['date'].tolist(),
        'direct_radiation': hourly_dataframe['direct_radiation'].tolist()
    }
    return jsonify(data)


# Web interface to manage Modbus servers
@app.route('/')
def home():
    from modbus_server import modbus_servers
    global server_config
    server_config = load_server_config()
    for server_id, server in modbus_servers.items():
        for server_cfg in server_config['servers']:
            if server_id == f"{server_cfg['type']}_{server_cfg['port']}":
                server['parameters_json'] = json.dumps(server_cfg['parameters'])
    return render_template('home.html', servers=modbus_servers, server_config=server_config)


# Help page
@app.route('/help')
def help():
    return render_template('help.html')

# empty page
@app.route('/empty')
def empty():
    return render_template('empty.html')
