async function atualizarDados() {
    const response = await fetch('/dados');
    const historico = await response.json();

    let tabela = document.getElementById('sensor-data');
    tabela.innerHTML = '';

    historico.forEach(grupo => {
        grupo.forEach(sensor => {
            let row = tabela.insertRow();
            row.insertCell(0).textContent = sensor.data_hora;
            row.insertCell(1).textContent = sensor.sensor;
            row.insertCell(2).textContent = sensor.temperatura.toFixed(2) + " °C";
        });
    });
}

// Atualiza os dados automaticamente a cada 5 segundos
setInterval(atualizarDados, 5000);
atualizarDados();
