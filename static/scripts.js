// static/scripts.js

// Object to store selected actions for each parameter
const actions = {};

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('create-server-button').addEventListener('click', function() {
        const serverTypeSelect = document.getElementById('server_type');
        const selectedOption = serverTypeSelect.options[serverTypeSelect.selectedIndex];
        const serverType = selectedOption.value;
        const port = selectedOption.dataset.port;
        const parameters = JSON.parse(selectedOption.dataset.parameters);
        const serverId = serverType.replace(/\s+/g, '_') + '_' + port;

        fetch('/api/create_server', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ server_id: serverId, address: '0.0.0.0', port: parseInt(port) })
        }).then(response => response.json()).then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                alert('Error creating server');
            }
        });
    });

    if (document.getElementsByClassName('tablinks').length > 0) {
        document.getElementsByClassName('tablinks')[0].click();
    }
    setInterval(updateRegisters, 5000); // Poll every 5 seconds
});

function stopServer(serverId) {
    fetch('/api/stop_server/' + serverId, {
        method: 'POST'
    }).then(response => response.json()).then(data => {
        if (data.status === 'success') {
            location.reload();
        } else {
            alert('Error stopping server');
        }
    });
}

function openServer(evt, serverId) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(serverId).style.display = "block";
    evt.currentTarget.className += " active";
    fetchRegisters(serverId);
}

function fetchRegisters(serverId) {
    const serverTypeSelect = document.getElementById('server_type');
    const selectedOption = serverTypeSelect.options[serverTypeSelect.selectedIndex];
    const parameters = JSON.parse(selectedOption.dataset.parameters);

    fetch(`/api/get_registers/${serverId}?parameters=${encodeURIComponent(JSON.stringify(parameters))}`)
        .then(response => response.json())
        .then(data => {
            const parametersDiv = document.getElementById(serverId + '-parameters');
            parametersDiv.innerHTML = '';

            parameters.forEach(param => {
                const paramDiv = document.createElement('div');
                paramDiv.innerHTML = `
                    <strong>${param.name}:</strong> 
                    <span id="${serverId}-${param.name}">${data[param.name]}</span>
                    <select id="${serverId}-${param.name}-action" onchange="setAction('${serverId}', '${param.name}', this.value)">
                        <option value="none">None</option>
                        <option value="random">Random</option>
                        <option value="increment">Increment</option>
                        <option value="reset">Reset</option>
                    </select>
                `;
                parametersDiv.appendChild(paramDiv);

                const input = document.createElement('input');
                input.type = 'number';
                input.value = data[param.name];
                input.className = 'register-input';
                input.id = `${serverId}-${param.name}-input`;
                input.addEventListener('change', () => updateRegister(serverId, param.name, param.address, param.function_code, input.value));
                parametersDiv.appendChild(input);

                // Restore the selected action from the actions object
                if (actions[serverId] && actions[serverId][param.name]) {
                    document.getElementById(`${serverId}-${param.name}-action`).value = actions[serverId][param.name];
                }
            });
        });
}

function setAction(serverId, paramName, action) {
    if (!actions[serverId]) {
        actions[serverId] = {};
    }
    actions[serverId][paramName] = action;

    // Call the REST API to set the action
    fetch(`/api/set_action/${serverId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ param_name: paramName, action: action })
    }).then(response => response.json()).then(data => {
        if (data.status !== 'success') {
            alert('Error setting action');
        }
    });
}

function updateRegister(serverId, name, address, function_code, value) {
    const payload = { name, address, function_code, value: parseInt(value) };
    fetch(`/api/set_register/${serverId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    }).then(response => response.json()).then(data => {
        if (data.status !== 'success') {
            alert('Error setting register value');
        }
    });
}

function updateRegisters() {
    var tablinks = document.getElementsByClassName('tablinks');
    for (var i = 0; i < tablinks.length; i++) {
        var serverId = tablinks[i].innerText;
        fetchRegisters(serverId);
    }
}