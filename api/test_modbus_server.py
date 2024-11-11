# test_modbus_server.py

import asyncio
import pytest
from modbus_server import create_modbus_server, stop_modbus_server, modbus_servers



@pytest.mark.asyncio
async def test_create_modbus_server():
    server_id = 'test_server'
    address = 'localhost'
    port = 5021

    # Create the Modbus server
    create_modbus_server(server_id, address, port)

    # Allow some time for the server to start
    await asyncio.sleep(1)

    # Check if the server is in the modbus_servers dictionary
    assert server_id in modbus_servers

    # Check if the server context is not None
    server_info = modbus_servers[server_id]
    assert server_info['context'] is not None
    assert server_info['port'] == port

    # Clean up by stopping the server
    stop_modbus_server(server_id)
    assert server_id not in modbus_servers
