async function atualizarDados() {
    const response = await fetch('/dados');
    const historico = await response.json();

    let tabela = document.getElementById('sensor-data');
    tabela.innerHTML = '';

    historico.forEach(sensor => {
        let row = tabela.insertRow();
        row.insertCell(0).textContent = sensor.data_hora;
        row.insertCell(1).textContent = sensor.canal;
        row.insertCell(2).textContent = sensor.sensor;
        row.insertCell(3).textContent = sensor.temperatura !== "Erro" ? sensor.temperatura.toFixed(2) + " °C" : "Erro";
    });
}

async function mudarCanal() {
    let canal = document.getElementById('canal').value;
    if (canal < 1 || canal > 16) {
        alert("Canal inválido! Escolha um entre 1 e 16.");
        return;
    }

    const response = await fetch(`/mudar_canal/${canal}`);
    const resultado = await response.json();
    alert(resultado.mensagem);
    atualizarDados(); // Atualiza a interface imediatamente
}

async function forcarLeitura() {
    const response = await fetch('/forcar_leitura');
    const resultado = await response.json();
    alert(resultado.mensagem);
    atualizarDados(); // Atualiza a interface imediatamente
}

// Atualiza os dados automaticamente a cada 5 segundos
setInterval(atualizarDados, 5000);
atualizarDados();
