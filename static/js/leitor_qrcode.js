const resultadoDiv = document.getElementById('resultado');
let processando = false;
let html5QrCode = null;
let cameraAtiva = false;

// Buscando os dados que foram injetados pelo HTML
const idAtividadeParaEnvio = window.ConfigAtividade.idAtividadeParaEnvio;

document.getElementById('formManual').addEventListener('submit', function (event) {
    event.preventDefault();
    const codigoManual = document.getElementById('codigoManual').value.trim();
    if (codigoManual) validarNoServidor(codigoManual);
});

async function validarNoServidor(codigoLido) {
    if (processando) return;
    processando = true;

    if (!idAtividadeParaEnvio || idAtividadeParaEnvio === "None") {
        exibirErro('🚨 Erro do Sistema', 'A página não carregou os dados da atividade. Atualize a página.');
        return;
    }

    resultadoDiv.innerHTML = '<span class="text-warning">⏳ Validando...</span>';
    resultadoDiv.className = 'processando';

    try {
        // Usando a URL e o Token vindos do objeto de configuração
        const response = await fetch(window.ConfigAtividade.urlIdentificar, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.ConfigAtividade.csrfToken
            },
            body: JSON.stringify({ codigo: codigoLido, atividade_id: idAtividadeParaEnvio })
        });

        if (!response.ok) {
            throw new Error(`HTTP Error ${response.status}`);
        }

        const dados = await response.json();

        if (dados.autorizado) {
            resultadoDiv.innerHTML = `<span class="text-success">✅ ${dados.mensagem} Redirecionando...</span>`;
            pararCameraSeAtiva();
            window.location.href = dados.redirect_url;
        } else {
            exibirErro('⛔ Acesso Negado', dados.mensagem);
        }
    } catch (err) {
        console.error('Erro na requisição:', err);
        exibirErro('📡 Sem Conexão', 'Não foi possível conectar ao servidor. Verifique a internet e tente novamente.');
    }
}

function exibirErro(titulo, mensagem) {
    resultadoDiv.innerHTML = `<strong>${titulo}</strong><br><small>${mensagem}</small>`;
    resultadoDiv.className = 'negado alert alert-danger mt-3';
    setTimeout(() => {
        resultadoDiv.textContent = '';
        resultadoDiv.className = '';
        processando = false;
    }, 4000);
}

function pararCameraSeAtiva() {
    if (html5QrCode && cameraAtiva) {
        html5QrCode.stop().then(() => cameraAtiva = false).catch(console.error);
    }
}

function onScanSuccess(decodedText) {
    if (!processando) validarNoServidor(decodedText);
}

try {
    const readerElem = document.getElementById('reader');
    if (typeof Html5Qrcode !== 'undefined' && readerElem) {
        html5QrCode = new Html5Qrcode('reader');
        html5QrCode
            .start(
                { facingMode: 'environment' },
                { fps: 10, qrbox: { width: 250, height: 250 } },
                onScanSuccess
            )
            .then(() => cameraAtiva = true)
            .catch((err) => {
                console.error(err);
                exibirErro('Erro na Câmera', 'Permissão negada ou câmera indisponível.');
            });
    }
} catch (err) {
    exibirErro('Erro Crítico', 'Falha ao carregar o leitor de QR Code.');
}