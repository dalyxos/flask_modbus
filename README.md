# Flask Modbus

A Flask application to manage Modbus servers.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Running with Docker](#running-with-docker)
- [REST API](#rest-api)
  - [Get All Servers](#get-all-servers)
  - [Get Server Details](#get-server-details)
  - [Add a New Server](#add-a-new-server)
  - [Update Server](#update-server)
  - [Delete Server](#delete-server)
- [License](#license)

## Introduction

This project provides a Flask-based web interface to manage Modbus servers. It allows you to start, stop, and configure Modbus servers through a web interface.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/dalyxos/flask_modbus.git
    cd flask_modbus
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the Flask application:
    ```sh
    flask run
    ```

2. Access the web interface at `http://127.0.0.1:8000`.

#***REMOVED***

You can configure the simulator by editing the `servers.json` file located in the `/app/data/` directory.

### Example `servers.json`:
```json
{
    "servers": [
        {
            "type": "Solax",
            "port": 5020,
            "parameters": [
                {
                    "name": "Voltage",
                    "address": 0,
                    "function_code": 3
                },
                {
                    "name": "Current",
                    "address": 1,
                    "function_code": 3
                },
                {
                    "name": "Power",
                    "address": 2,
                    "function_code": 3
                },
                {
                    "name": "Set Mode",
                    "address": 10,
                    "function_code": 6
                }
            ]
        },
        {
            "type": "ChargingStation",
            "port": 5030,
            "parameters": [
                {
                    "name": "Charge Status",
                    "address": 0,
                    "function_code": 3
                },
                {
                    "name": "Battery Level",
                    "address": 1,
                    "function_code": 3
                },
                {
                    "name": "Set Charge Rate",
                    "address": 10,
                    "function_code": 6
                }
            ]
        }
    ]
}
```

## Running with Docker
To run the Docker container, exposing the necessary port and mounting the volume for configuration files, use the following command:
   ```bash
   # Linux
   docker run -d -p 8000:8000 -v $(pwd)/app/data:/app/data --name flask_modbus_container flask_modbus
   ```
   ```PS
   # Windows
   docker run -d -p 8000:8000 -v ${pwd}/app/data:/app/data --name flask_modbus_container flask_modbus
   ```
* `-d`: Run the container in detached mode.
* `-p 8000:8000`: Map port 8000 on the host to port 8000 in the container.
* `-v $(pwd)/app/data:/app/data`: Mount the app/data directory from the host to the container.
* `--name flask_modbus_container`: Name the container flask_modbus_container.
* `dalyxos/modbus_simulator:latest`: The name of the Docker image.

## REST API
The Flask Modbus application provides a REST API to interact with the Modbus servers. Below are the available endpoints:

### Get All Servers
* Endpoint: `/api/servers`
* Method: `GET`
* Description: Retrieves a list of all configured Modbus servers.
* Response:
```json
[
    {
        "type": "Solax",
        "port": 5020,
        "parameters": [
            {
                "name": "Voltage",
                "address": 0,
                "function_code": 3
            },
            ...
        ]
    },
    ...
]
```
### Get Server Details
* Endpoint: `/api/servers/<server_id>`
* Method: `GET`
* Description: Retrieves details of specific Modbus server.
* Response:
```json
{
    "type": "Solax",
    "port": 5020,
    "parameters": [
        {
            "name": "Voltage",
            "address": 0,
            "function_code": 3
        },
        ...
    ]
}
```
### Add a New Server
* Endpoint: `/api/servers`
* Method: `POST`
* Description: Adds a new Modbus server.
* Request Body:
```json
{
    "type": "Solax",
    "port": 5020,
    "parameters": [
        {
            "name": "Voltage",
            "address": 0,
            "function_code": 3
        },
        ...
    ]
}
```
* Response:
```json
{
    "message": "Server added successfully"
}
```
### Update Server
* Endpoint: `/api/servers/<server_id>`
* Method: `PUT`
* Description: Updates an existing Modbus server.
* Request Body:
```json
{
    "type": "Solax",
    "port": 5020,
    "parameters": [
        {
            "name": "Voltage",
            "address": 0,
            "function_code": 3
        },
        ...
    ]
}
```
* Response:
```json
{
    "message": "Server updated successfully"
}
```
### Delete Server
* Endpoint: `/api/servers/<server_id>`
* Method: `DELETE`
* Description: Deletes a specific Modbus server.
* Response:
```json
{
    "message": "Server deleted successfully"
}
```
## License

This project is licensed under the MIT License.