# routes.py
from flask import Flask, request, jsonify, render_template
from modbus_server import create_modbus_server, stop_modbus_server, get_modbus_server_context
***REMOVED***
import os

app = Flask(__name__)

# Load server configuration from JSON file
def load_server_config():
    with open('./config/servers.json') as f:
        return json.load(f)

# REST API to create a new Modbus server
@app.route('/api/create_server', methods=['POST'])
def api_create_server():
    data = request.json
    server_id = data['server_id']
    address = data['address']
    port = data['port']
    create_modbus_server(server_id, address, port)
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
        hr_values = context[0].getValues(3, 0, count=10)
        ir_values = context[0].getValues(4, 0, count=10)
        fc6_values = context[0].getValues(6, 0, count=10)
        return jsonify({'hr': hr_values, 'ir': ir_values, 'fc6': fc6_values})
    else:
        return jsonify({'status': 'error', 'message': 'Server not found'}), 404

# REST API to set a single register value for a Modbus server
@app.route('/api/set_register/<server_id>', methods=['POST'])
def api_set_register(server_id):
    context = get_modbus_server_context(server_id)
    if context:
        data = request.json
        reg_type = data['type']
        index = data['index']
        value = data['value']
        if reg_type == 'hr':
            context[0].setValues(3, index, [value])
        elif reg_type == 'ir':
            context[0].setValues(4, index, [value])
        elif reg_type == 'fc6':
            context[0].setValues(6, index, [value])
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Server not found'}), 404

# Web interface to manage Modbus servers
@app.route('/')
def home():
    from modbus_server import modbus_servers
    server_config = load_server_config()
    return render_template('home.html', servers=modbus_servers, server_config=server_config)