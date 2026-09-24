document.addEventListener('DOMContentLoaded', function () {
    // 1. Obter dados enviados pelo Django (no contexto global do HTML)
    let participantes = window.participantesData || [];
    let premiosOriginais = window.premiosData || [];

    // Monta o pool expandido de prêmios de acordo com as quantidades cadastradas
    let poolPremios = [];
    premiosOriginais.forEach(p => {
        const qtd = parseInt(p.quantidade, 10) || 1;
        for (let i = 0; i < qtd; i++) {
            poolPremios.push(p.nome);
        }
    });

    // 2. Mapeamento de Elementos do DOM
    const btnSorteio = document.getElementById('btnSorteio');
    const btnFullscreen = document.getElementById('btnFullscreen');
    const btnReiniciar = document.getElementById('btnReiniciar');
    const statusText = document.getElementById('statusText');
    const piaoCard = document.getElementById('piaoCard');
    const track = document.getElementById('horizontalTrack');
    const wrapper = document.getElementById('horizontalWrapper');
    const listaHistorico = document.getElementById('listaHistorico');
    const msgVazio = document.getElementById('msgVazio');
    const totalParticipantesEl = document.getElementById('totalParticipantes');
    const nomePremioAtualEl = document.getElementById('nomePremioAtual');

    let estaRodando = false;
    let contadorSorteios = 0;
    let premioSorteadoAtual = null;
    let intervalEmbaralharPremio = null;

    // Retorna a largura total dos cards ajustada para Tela Cheia (420px + 20px de margem)
    function getItemTotalWidth() {
    const isFS = document.fullscreenElement !== null;
    return (isFS ? 700 : 280) + 20; // 700px de largura + 20px de margem em ecrã inteiro
}

    if (totalParticipantesEl) {
        totalParticipantesEl.innerText = participantes.length;
    }

    // 3. Efeitos Sonoros via Web Audio API
    let audioCtx;
    function getAudioContext() {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        return audioCtx;
    }

    function tocarTick() {
        try {
            const ctx = getAudioContext();
            if (ctx.state === 'suspended') ctx.resume();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(440, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(110, ctx.currentTime + 0.03);
            gain.gain.setValueAtTime(0.08, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.03);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.03);
        } catch (e) {}
    }

    function tocarFanfarra() {
        try {
            const ctx = getAudioContext();
            if (ctx.state === 'suspended') ctx.resume();
            const notas = [261.63, 329.63, 392.00, 523.25, 659.25];
            notas.forEach((freq, idx) => {
                setTimeout(() => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(freq, ctx.currentTime);
                    gain.gain.setValueAtTime(0.2, ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.4);
                }, idx * 100);
            });
        } catch (e) {}
    }

    // 4. Construção da Esteira de Participantes
    let listaEsteira = [];
    function construirEsteira() {
        if (!track) return;
        track.innerHTML = '';
        listaEsteira = [];

        if (participantes.length === 0) {
            track.innerHTML = '<div class="item-participante text-white-50">Sem participantes</div>';
            return;
        }

        const repeticoes = Math.max(15, Math.ceil(80 / participantes.length));
        for (let r = 0; r < repeticoes; r++) {
            participantes.forEach((nome) => listaEsteira.push(nome));
        }

        listaEsteira.forEach((nome, index) => {
            const div = document.createElement('div');
            div.className = 'item-participante';
            div.dataset.index = index;
            div.innerText = nome;
            track.appendChild(div);
        });

        posicionarNoItem(0);
    }

    function posicionarNoItem(index) {
        const itemTotalWidth = getItemTotalWidth();
        const wrapperWidth = wrapper ? wrapper.offsetWidth : 800;
        const centroWrapper = wrapperWidth / 2;
        const offsetItem = (index * itemTotalWidth) + (itemTotalWidth / 2);
        const targetX = centroWrapper - offsetItem;
        track.style.transform = `translateX(${targetX}px)`;
    }

    // 5. Atualização Dinâmica do Painel Flutuante de Prêmios (Tela Cheia)
    function atualizarListasPremiosUI() {
        const contagem = {};
        poolPremios.forEach(nome => {
            contagem[nome] = (contagem[nome] || 0) + 1;
        });

        const floatPanelList = document.querySelector('.fullscreen-prizes-panel ul');
        if (floatPanelList) {
            floatPanelList.innerHTML = '';
            const nomes = Object.keys(contagem);
            if (nomes.length === 0) {
                floatPanelList.innerHTML = '<li class="text-white-50 py-2">Todos os prêmios foram sorteados!</li>';
            } else {
                nomes.forEach(nome => {
                    const li = document.createElement('li');
                    li.className = 'd-flex justify-content-between align-items-center py-2';
                    li.innerHTML = `
                        <span class="text-truncate text-white" style="max-width: 140px;" title="${nome}">🎁 ${nome}</span>
                        <span class="badge bg-light text-dark fw-bold">${contagem[nome]} un.</span>
                    `;
                    floatPanelList.appendChild(li);
                });
            }
        }
    }

    // 6. Animação de Giro do Sorteio
    function rodarPiaoHorizontal() {
        if (estaRodando) return;

        if (participantes.length === 0) {
            alert("Todos os participantes já foram sorteados!");
            return;
        }

        estaRodando = true;
        if (btnSorteio) btnSorteio.disabled = true;

        // Escolhe o prêmio do sorteio
        let indexPremioSorteado = -1;
        if (poolPremios.length > 0) {
            indexPremioSorteado = Math.floor(Math.random() * poolPremios.length);
            premioSorteadoAtual = poolPremios[indexPremioSorteado];
        } else {
            premioSorteadoAtual = "Brinde Surpresa";
        }

        // Animação visual de troca dos prêmios no título
        if (nomePremioAtualEl) {
            intervalEmbaralharPremio = setInterval(() => {
                if (poolPremios.length > 0) {
                    const nomeTemp = poolPremios[Math.floor(Math.random() * poolPremios.length)];
                    nomePremioAtualEl.innerHTML = `🎲 <span class="text-white">${nomeTemp}</span>`;
                }
            }, 80);
        }

        if (statusText) statusText.innerText = "Sorteando participante e prêmio...";

        const antigoVencedor = track.querySelector('.vencedor');
        if (antigoVencedor) antigoVencedor.classList.remove('vencedor');

        const ganhadorIndexOriginal = Math.floor(Math.random() * participantes.length);
        const ganhadorNome = participantes[ganhadorIndexOriginal];

        const itemTotalWidth = getItemTotalWidth();
        const minIndiceParada = Math.min(40, listaEsteira.length - participantes.length);
        let targetIndex = -1;

        for (let i = minIndiceParada; i < listaEsteira.length; i++) {
            if (listaEsteira[i] === ganhadorNome) {
                targetIndex = i;
                break;
            }
        }

        if (targetIndex === -1) targetIndex = ganhadorIndexOriginal;

        const wrapperWidth = wrapper.offsetWidth;
        const centroWrapper = wrapperWidth / 2;
        const targetPos = centroWrapper - ((targetIndex * itemTotalWidth) + (itemTotalWidth / 2));

        let currentX = centroWrapper - (itemTotalWidth / 2);
        let duracaoTotal = 5500;
        let startTime = null;
        let ultimoItemIndexTick = -1;

        function animar(timestamp) {
            if (!startTime) startTime = timestamp;
            let progresso = (timestamp - startTime) / duracaoTotal;

            if (progresso > 1) progresso = 1;

            let ease = 1 - Math.pow(1 - progresso, 3);
            let posX = currentX + (targetPos - currentX) * ease;

            track.style.transform = `translateX(${posX}px)`;

            let itemAtualNoCentro = Math.floor((centroWrapper - posX) / itemTotalWidth);
            if (itemAtualNoCentro !== ultimoItemIndexTick && itemAtualNoCentro >= 0) {
                tocarTick();
                ultimoItemIndexTick = itemAtualNoCentro;
            }

            if (progresso < 1) {
                requestAnimationFrame(animar);
            } else {
                finalizarSorteio(ganhadorIndexOriginal, targetIndex, indexPremioSorteado);
            }
        }

        requestAnimationFrame(animar);
    }

    // 7. Finalização e Apresentação do Vencedor
    function finalizarSorteio(originalIndex, targetIndex, indexPremioSorteado) {
        if (intervalEmbaralharPremio) {
            clearInterval(intervalEmbaralharPremio);
        }

        if (nomePremioAtualEl) {
            nomePremioAtualEl.innerHTML = `🎁 <span class="text-warning fw-bold fs-4">${premioSorteadoAtual}</span>`;
        }

        const ganhador = participantes[originalIndex];

        const cardSorteado = track.children[targetIndex];
        if (cardSorteado) cardSorteado.classList.add('vencedor');

        // Atualiza a lista de elegíveis
        participantes.splice(originalIndex, 1);
        if (totalParticipantesEl) totalParticipantesEl.innerText = participantes.length;

        // Atualiza os prêmios disponíveis
        if (indexPremioSorteado >= 0 && poolPremios.length > 0) {
            poolPremios.splice(indexPremioSorteado, 1);
            atualizarListasPremiosUI();
        }

        estaRodando = false;
        if (btnSorteio) btnSorteio.disabled = false;

        if (statusText) {
            statusText.innerHTML = `GANHADOR(A): <strong class="text-white fs-2 d-block mt-1">${ganhador.toUpperCase()}</strong>`;
        }
        tocarFanfarra();

        if (typeof confetti === 'function') {
            confetti({ particleCount: 150, spread: 100, origin: { y: 0.5 } });
        }

        contadorSorteios++;
        if (msgVazio) msgVazio.classList.add('d-none');

        if (listaHistorico) {
            const itemLista = document.createElement('li');
            itemLista.className = 'list-group-item d-flex justify-content-between align-items-center py-3';
            itemLista.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi bi-trophy-fill text-warning fs-3 me-3"></i>
                    <div>
                        <strong class="text-dark d-block fs-5">${ganhador}</strong>
                        <small class="text-muted">Prêmio Ganho: <strong class="text-success">${premioSorteadoAtual}</strong></small>
                    </div>
                </div>
                <span class="badge bg-success border px-3 py-2">${contadorSorteios}º Sorteio</span>
            `;
            listaHistorico.prepend(itemLista);
        }
    }

    // 8. Ativação da Tela Cheia Exclusiva no #piaoCard
    if (btnFullscreen && piaoCard) {
        btnFullscreen.addEventListener('click', function () {
            if (!document.fullscreenElement) {
                if (piaoCard.requestFullscreen) {
                    piaoCard.requestFullscreen();
                } else if (piaoCard.webkitRequestFullscreen) {
                    piaoCard.webkitRequestFullscreen();
                } else if (piaoCard.msRequestFullscreen) {
                    piaoCard.msRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        });
    }

    // Recalcula o posicionamento da esteira quando entra/sai do modo Tela Cheia
    document.addEventListener('fullscreenchange', function () {
        if (!estaRodando) {
            posicionarNoItem(0);
        }
    });

    // 9. Inicialização Geral
    construirEsteira();

    if (btnSorteio) btnSorteio.addEventListener('click', rodarPiaoHorizontal);

    if (btnReiniciar) {
        btnReiniciar.addEventListener('click', function () {
            if (confirm("Deseja reiniciar a tela de sorteio?")) {
                window.location.reload();
            }
        });
    }

    window.addEventListener('resize', function () {
        if (!estaRodando) posicionarNoItem(0);
    });
});