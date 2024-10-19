#! /usr/bin/env python3

from flask import Flask, render_template, request, jsonify
from pymodbus.datastore import ModbusSlaveContext, ModbusSequentialDataBlock, ModbusServerContext
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification
import asyncio
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

app = Flask(__name__)

# Dictionary to store Modbus server instances
modbus_servers = {}

# Function to create and start a Modbus server
def create_modbus_server(server_id, address, port):
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [0]*100),
        ir=ModbusSequentialDataBlock(0, [0]*100))
    store.register(6, 'fc6', ModbusSequentialDataBlock(0, [0]*100))  # Data block for function code 6
    
    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    async def run_server():
        await StartAsyncTcpServer(
            context=context,
            identity=identity,
            address=(address, port)
        )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server_task = loop.create_task(run_server())
    server_thread = threading.Thread(target=loop.run_forever)
    server_thread.daemon = True
    server_thread.start()

    modbus_servers[server_id] = {
        'context': context,
        'thread': server_thread,
        'loop': loop,
        'task': server_task
    }

# Callback for when a Modbus master connects
def on_connect(client):
    log.info(f"Modbus master connected: {client}")

# Callback for when a Modbus master disconnects
def on_disconnect(client):
    log.info(f"Modbus master disconnected: {client}")

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
    if server_id in modbus_servers:
        server_info = modbus_servers[server_id]
        server_info['loop'].call_soon_threadsafe(server_info['loop'].stop)
        server_info['thread'].join()
        del modbus_servers[server_id]
        return jsonify({'status': 'success', 'server_id': server_id})
    else:
        return jsonify({'status': 'error', 'message': 'Server not found'}), 404

# REST API to get register values for a Modbus server
@app.route('/api/get_registers/<server_id>', methods=['GET'])
def api_get_registers(server_id):
    if server_id in modbus_servers:
        server_info = modbus_servers[server_id]
        context = server_info['context']
        hr_values = context[0].getValues(3, 0, count=10)
        ir_values = context[0].getValues(4, 0, count=10)
        fc6_values = context[0].getValues(6, 0, count=10)
        return jsonify({'hr': hr_values, 'ir': ir_values, 'fc6': fc6_values})
    else:
        return jsonify({'status': 'error', 'message': 'Server not found'}), 404

# REST API to set register values for a Modbus server
@app.route('/api/set_registers/<server_id>', methods=['POST'])
def api_set_registers(server_id):
    if server_id in modbus_servers:
        server_info = modbus_servers[server_id]
        context = server_info['context']
        data = request.json
        hr_values = data['hr']
        ir_values = data['ir']
        context[0].setValues(3, 0, hr_values)
        context[0].setValues(4, 0, ir_values)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Server not found'}), 404

# REST API to set a single register value for a Modbus server
@app.route('/api/set_register/<server_id>', methods=['POST'])
def api_set_register(server_id):
    if server_id in modbus_servers:
        server_info = modbus_servers[server_id]
        context = server_info['context']
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
    return render_template('home.html', servers=modbus_servers)

def main():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    main()