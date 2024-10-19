
document.getElementById('create-server-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const serverId = document.getElementById('server_id').value;
    const address = document.getElementById('address').value;
    const port = document.getElementById('port').value;
    fetch('/api/create_server', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ server_id: serverId, address: address, port: port })
    }).then(response => response.json()).then(data => {
        if (data.status === 'success') {
            location.reload();
        } else {
            alert('Error creating server');
        }
    });
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

function submitRegisters(serverId) {
    const hrInputs = document.querySelectorAll(`#${serverId}-edit-hr input`);
    const irInputs = document.querySelectorAll(`#${serverId}-edit-ir input`);
    const fc6Inputs = document.querySelectorAll(`#${serverId}-edit-fc6 input`);
    const hrValues = Array.from(hrInputs).map(input => parseInt(input.value));
    const irValues = Array.from(irInputs).map(input => parseInt(input.value));
    const fc6Values = Array.from(fc6Inputs).map(input => parseInt(input.value));

    fetch('/api/set_registers/' + serverId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ hr: hrValues, ir: irValues, fc6: fc6Values })
    }).then(response => response.json()).then(data => {
        if (data.status === 'success') {
            fetchRegisters(serverId);
        } else {
            alert('Error setting registers');
        }
    });
}

// Open the first tab by default
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementsByClassName('tablinks').length > 0) {
        document.getElementsByClassName('tablinks')[0].click();
    }
    setInterval(updateRegisters, 5000); // Poll every 5 seconds
});

function updateRegisters() {
    var tablinks = document.getElementsByClassName('tablinks');
    for (var i = 0; i < tablinks.length; i++) {
        var serverId = tablinks[i].innerText;
        fetchRegisters(serverId);
    }
}