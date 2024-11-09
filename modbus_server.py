# modbus_server.py

import asyncio
import threading
import logging
from pymodbus.datastore import ModbusSlaveContext, ModbusSequentialDataBlock, ModbusServerContext
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification

# Configure logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

# Dictionary to store Modbus server instances
modbus_servers = {}


# Callback for when a Modbus master connects
def on_connect(client):
    log.info(f"Modbus master connected: {client}")


# Callback for when a Modbus master disconnects
def on_disconnect(client):
    log.info(f"Modbus master disconnected: {client}")


# Function to create and start a Modbus server
def create_modbus_server(server_id, address, port, parameters={}):
    max_hr_address = 100
    max_ir_address = 100
    max_fc6_address = 100
    print(f'parameters: {parameters}')
    for item in parameters:
        print(f'item: {item}')
        if item['function_code'] == 3 and item['address'] > max_hr_address:
            max_hr_address = item['address'] + 10
        elif item['function_code'] == 4 and item['address'] > max_ir_address:
            max_ir_address = item['address'] + 10
        elif item['function_code'] == 6 and item['address'] > max_fc6_address:
            max_fc6_address = item['address'] + 10

    print(f'max_hr_address: {max_hr_address}')
    print(f'max_ir_address: {max_ir_address}')
    print(f'max_fc6_address: {max_fc6_address}')

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [0]*max_hr_address),
        ir=ModbusSequentialDataBlock(0, [0]*max_ir_address))
    store.register(6, 'fc6', ModbusSequentialDataBlock(0, [0]*max_fc6_address))  # Data block for function code 6

    set_default_values(store, parameters)

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
        'task': server_task,
        'port': port,
        'parameters': parameters
    }


def stop_modbus_server(server_id):
    if server_id in modbus_servers:
        server_info = modbus_servers[server_id]
        server_info['loop'].call_soon_threadsafe(server_info['loop'].stop)
        server_info['thread'].join()
        del modbus_servers[server_id]
        return True
    return False


def get_modbus_server_context(server_id):
    if server_id in modbus_servers:
        return modbus_servers[server_id]['context']
    return None

def get_modbus_server_parameters(server_id):
    if server_id in modbus_servers:
        return modbus_servers[server_id]['parameters']
    return None

def get_modbus_server_parameter_value(server_id, name):
    param = find_parameter_by_name(server_id, name)
    if param:
        fc, address = param['function_code'], param['address']
        count = determine_count(param)
        values = get_modbus_server_context(server_id)[0].getValues(fc, address, count=count)
        return parse_values(param, values)
    return None

def set_modbus_server_parameter_value(server_id, name, value):
    param = find_parameter_by_name(server_id, name)
    if param:
        fc, address = param['function_code'], param['address']
        count = determine_count(param)
        values = [value]
        set_default_values(get_modbus_server_context(server_id)[0], [param])
        get_modbus_server_context(server_id)[0].setValues(fc, address, values)
        return True
    return False

def find_parameter_by_name(server_id, name):
    for param in get_modbus_server_parameters(server_id):
        if param['name'] == name:
            return param
    return None

def determine_count(param):
    if param['type'] == 'string':
        return param['size']
    elif param['type'] in ['u64', 'i64']:
        return 4
    elif param['type'] in ['u32', 'i32', 'float']:
        return 2
    return 1

def parse_values(param, values):
    if '16' in param['type']:
        return values[0]
    elif '32' in param['type']:
        return (values[1] << 16) | values[0]
    elif '64' in param['type']:
        return (values[3] << 48) | (values[2] << 32) | (values[1] << 16) | values[0]
    elif param['type'] == 'float':
        import struct
        packed = struct.pack('>HH', values[0], values[1])
        return struct.unpack('>f', packed)[0]
    elif param['type'] == 'string':
        return ''.join(chr(v) for v in values).rstrip('\x00')
    return None

def set_default_values(store, parameters):
    for param in parameters:
        fc = param['function_code']
        address = param['address']
        default = param['default']
        if '16' in param:
            store.setValues(fc, address, [default])
        elif '32' in param['type']:
            store.setValues(fc, address, [default & 0xFFFF, (default >> 16) & 0xFFFF])
        elif param['type'] == 'u64':
            store.setValues(fc, address, [default & 0xFFFF, (default >> 16) & 0xFFFF, (default >> 32) & 0xFFFF, (default >> 48) & 0xFFFF])
        elif param['type'] == 'float':
            import struct
            packed = struct.pack('>f', default)
            unpacked = struct.unpack('>HH', packed)
            store.setValues(fc, address, list(unpacked))
        elif param['type'] == 'string':
            values = [ord(c) for c in default.ljust(param['size'], '\x00')]
            store.setValues(fc, address, values)
