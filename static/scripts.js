// static/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('create-server-button').addEventListener('click', function() {
        const serverTypeSelect = document.getElementById('server_type');
        const selectedOption = serverTypeSelect.options[serverTypeSelect.selectedIndex];
        const serverType = selectedOption.value;
        const port = selectedOption.dataset.port;
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
    fetch('/api/get_registers/' + serverId)
        .then(response => response.json())
        .then(data => {
            document.getElementById(serverId + '-hr').innerText = data.hr.join(', ');
            document.getElementById(serverId + '-ir').innerText = data.ir.join(', ');
            document.getElementById(serverId + '-fc6').innerText = data.fc6.join(', ');

            // Create input fields for editing registers
            const hrEditDiv = document.getElementById(serverId + '-edit-hr');
            hrEditDiv.innerHTML = '';
            data.hr.forEach((value, index) => {
                const input = document.createElement('input');
                input.type = 'number';
                input.value = value;
                input.className = 'register-input';
                input.id = serverId + '-hr-' + index;
                input.addEventListener('change', () => updateRegister(serverId, 'hr', index, input.value));
                hrEditDiv.appendChild(input);
            });

            const irEditDiv = document.getElementById(serverId + '-edit-ir');
            irEditDiv.innerHTML = '';
            data.ir.forEach((value, index) => {
                const input = document.createElement('input');
                input.type = 'number';
                input.value = value;
                input.className = 'register-input';
                input.id = serverId + '-ir-' + index;
                input.addEventListener('change', () => updateRegister(serverId, 'ir', index, input.value));
                irEditDiv.appendChild(input);
            });

            const fc6EditDiv = document.getElementById(serverId + '-edit-fc6');
            fc6EditDiv.innerHTML = '';
            data.fc6.forEach((value, index) => {
                const input = document.createElement('input');
                input.type = 'number';
                input.value = value;
                input.className = 'register-input';
                input.id = serverId + '-fc6-' + index;
                input.addEventListener('change', () => updateRegister(serverId, 'fc6', index, input.value));
                fc6EditDiv.appendChild(input);
            });
        });
}

function updateRegister(serverId, type, index, value) {
    const payload = { type, index, value: parseInt(value) };
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