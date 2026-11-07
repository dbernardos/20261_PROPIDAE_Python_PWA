document.addEventListener('DOMContentLoaded', function () {
    let participantes = window.participantesData || [];
    let premiosOriginais = window.premiosData || [];

    let poolPremios = [];
    premiosOriginais.forEach(p => {
        const qtd = parseInt(p.quantidade, 10) || 1;
        for (let i = 0; i < qtd; i++) {
            poolPremios.push(p.nome);
        }
    });

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
    let premioSorteadoAtual = null;
    let intervalEmbaralharPremio = null;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function getItemTotalWidth() {
        const isFS = document.fullscreenElement !== null;
        return (isFS ? 700 : 280) + 20;
    }

    if (totalParticipantesEl) {
        totalParticipantesEl.innerText = participantes.length;
    }

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

    function atualizarListasPremiosUI() {
        const contagem = {};
        poolPremios.forEach(nome => {
            contagem[nome] = (contagem[nome] || 0) + 1;
        });

        const nomes = Object.keys(contagem);

        // 1. Atualiza a lista da coluna da esquerda
        const listaEsquerda = document.getElementById('listaPremiosEsquerda');
        if (listaEsquerda) {
            listaEsquerda.innerHTML = '';
            if (nomes.length === 0) {
                listaEsquerda.innerHTML = '<li class="list-group-item text-muted px-0 py-3 text-center">Todos os prêmios foram sorteados!</li>';
            } else {
                nomes.forEach(nome => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item d-flex justify-content-between align-items-center px-0';
                    li.innerHTML = `
                        🎁 ${nome}
                        <span class="badge bg-success rounded-pill">${contagem[nome]} unidade(s)</span>
                    `;
                    listaEsquerda.appendChild(li);
                });
            }
        }

        // 2. Atualiza o painel de tela cheia
        const floatPanelList = document.querySelector('.fullscreen-prizes-panel ul');
        if (floatPanelList) {
            floatPanelList.innerHTML = '';
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

    function adicionarAoHistorico(ganhador, premio) {
        if (msgVazio) msgVazio.style.display = 'none';
        if (listaHistorico) {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.innerHTML = `
                <span><strong>👤 ${ganhador}</strong></span>
                <span class="badge bg-warning text-dark">🎁 ${premio}</span>
            `;
            listaHistorico.insertBefore(li, listaHistorico.firstChild);
        }
    }

    function rodarPiaoHorizontal() {
        if (estaRodando) return;

        if (participantes.length === 0) {
            alert("Todos os participantes elegíveis já foram sorteados!");
            return;
        }

        if (poolPremios.length === 0) {
            alert("Todos os prêmios cadastrados já foram sorteados!");
            return;
        }

        estaRodando = true;
        if (btnSorteio) btnSorteio.disabled = true;

        const indexPremioSorteado = Math.floor(Math.random() * poolPremios.length);
        premioSorteadoAtual = poolPremios[indexPremioSorteado];

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
        const minRepeticoes = 5;
        const targetIndexInTrack = (participantes.length * minRepeticoes) + ganhadorIndexOriginal;

        const wrapperWidth = wrapper ? wrapper.offsetWidth : 800;
        const centroWrapper = wrapperWidth / 2;
        const offsetTarget = (targetIndexInTrack * itemTotalWidth) + (itemTotalWidth / 2);
        const finalX = centroWrapper - offsetTarget;

        track.style.transition = 'none';
        track.style.transform = 'translateX(0px)';
        track.offsetHeight;

        track.style.transition = 'transform 6s cubic-bezier(0.15, 0.90, 0.25, 1.00)';
        track.style.transform = `translateX(${finalX}px)`;

        let tickInterval = setInterval(() => {
            tocarTick();
        }, 120);

        setTimeout(() => {
            clearInterval(tickInterval);
        }, 4500);

        setTimeout(() => {
            clearInterval(intervalEmbaralharPremio);
            if (nomePremioAtualEl) {
                nomePremioAtualEl.innerHTML = `🎁 <span class="text-warning fw-bold">${premioSorteadoAtual}</span>`;
            }

            const itemElement = track.querySelector(`[data-index="${targetIndexInTrack}"]`);
            if (itemElement) itemElement.classList.add('vencedor');

            if (statusText) {
                statusText.innerText = `🎉 GANHADOR(A): ${ganhadorNome.toUpperCase()}!`;
            }

            tocarFanfarra();
            if (typeof confetti === 'function') {
                confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
            }

            // 1. Remove da memória local do navegador
            participantes.splice(ganhadorIndexOriginal, 1);
            poolPremios.splice(indexPremioSorteado, 1);

            // 2. Atualiza os elementos da interface visual
            if (totalParticipantesEl) {
                totalParticipantesEl.innerText = participantes.length;
            }
            atualizarListasPremiosUI();
            adicionarAoHistorico(ganhadorNome, premioSorteadoAtual);

            // 3. Envia baixa para o Banco de Dados (Django) via URL gerada pelo template
            const pathSegs = window.location.pathname.split('/').filter(Boolean);
            const atividadeId = window.atividadeId || pathSegs[pathSegs.length - 2] || pathSegs[pathSegs.length - 1];
            const urlBaixa = window.urlBaixaSorteio || `/eventos/atividade/${atividadeId}/sorteio/baixa/`;

            fetch(urlBaixa, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    ganhador_nome: ganhadorNome,
                    premio_nome: premioSorteadoAtual
                })
            })
            .then(res => {
                if (!res.ok) console.error("Erro na resposta da baixa:", res.statusText);
            })
            .catch(err => console.error("Erro ao dar baixa no banco de dados:", err));

            // 4. Reconstrói a esteira sem o ganhador após 2.5 segundos
            setTimeout(() => {
                construirEsteira();
                estaRodando = false;

                if (participantes.length === 0 || poolPremios.length === 0) {
                    if (btnSorteio) btnSorteio.disabled = true;
                    if (statusText) {
                        statusText.innerText = poolPremios.length === 0 
                            ? "🏆 TODOS OS PRÊMIOS FORAM SORTEADOS!" 
                            : "⚠️ TODOS OS PARTICIPANTES FORAM SORTEADOS!";
                    }
                } else {
                    if (btnSorteio) btnSorteio.disabled = false;
                    if (statusText) statusText.innerText = "PRONTO PARA O PRÓXIMO SORTEIO!";
                }
            }, 2500);

        }, 6000);
    }

    construirEsteira();
    atualizarListasPremiosUI();

    if (btnSorteio) {
        btnSorteio.addEventListener('click', rodarPiaoHorizontal);
    }

    if (btnFullscreen && piaoCard) {
        btnFullscreen.addEventListener('click', function () {
            if (!document.fullscreenElement) {
                piaoCard.requestFullscreen().catch(err => alert(`Erro: ${err.message}`));
            } else {
                document.exitFullscreen();
            }
        });
    }

    if (btnReiniciar) {
        btnReiniciar.addEventListener('click', function () {
            location.reload();
        });
    }
});