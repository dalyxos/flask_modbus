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
        'task': server_task,
        'port': port
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
