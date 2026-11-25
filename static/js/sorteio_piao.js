document.addEventListener('DOMContentLoaded', function () {
  // Gerador de inteiros aleatórios criptograficamente seguro (sem viés de módulo)
  function randomInt(max) {
    if (max <= 1) return 0;
    if (window.crypto && window.crypto.getRandomValues) {
      const maxUint32 = 0xffffffff;
      const limit = maxUint32 - (maxUint32 % max);
      const buffer = new Uint32Array(1);
      let valor;
      do {
        window.crypto.getRandomValues(buffer);
        valor = buffer[0];
      } while (valor >= limit);
      return valor % max;
    }
    return Math.floor(Math.random() * max);
  }

  // Embaralhamento Fisher-Yates para distribuição uniforme
  function embaralharArray(lista) {
    const copia = [...lista];
    for (let i = copia.length - 1; i > 0; i--) {
      const j = randomInt(i + 1);
      [copia[i], copia[j]] = [copia[j], copia[i]];
    }
    return copia;
  }

  const participantesIniciais = [...(window.participantesData || [])];
  let participantes = embaralharArray(participantesIniciais);

  const premiosOriginais = window.premiosData || [];
  let poolPremios = [];
  premiosOriginais.forEach((p) => {
    const qtd = parseInt(p.quantidade, 10) || 1;
    for (let i = 0; i < qtd; i++) {
      poolPremios.push(p.nome);
    }
  });
  poolPremios = embaralharArray(poolPremios);

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
  const confettiCanvas = document.getElementById('confettiCanvas');

  const lancarConfetes =
    typeof confetti === 'function' && confettiCanvas
      ? confetti.create(confettiCanvas, { resize: true, useWorker: false })
      : null;

  let estaRodando = false;
  let indiceAtual = 0;
  let premioSorteadoAtual = null;
  let intervalEmbaralharPremio = null;
  let timerAnimacao = null;
  let timerProximaRodada = null;
  let rafSyncId = null;
  let audioCtx = null;

  function escapeHtml(texto) {
    return String(texto ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function getCookie(name) {
    if (!document.cookie) return null;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return null;
  }

  function resolverUrlBaixa() {
    if (window.urlBaixaSorteio) return window.urlBaixaSorteio;
    if (window.atividadeId) {
      return `/eventos/atividade/${window.atividadeId}/sorteio/baixa/`;
    }
    const pathSegs = window.location.pathname.split('/').filter(Boolean);
    const idNumerico = pathSegs.find((seg) => /^\d+$/.test(seg));
    const atividadeId = idNumerico || pathSegs[pathSegs.length - 1];
    return `/eventos/atividade/${atividadeId}/sorteio/baixa/`;
  }

  function notificarErroBaixa(ganhador, premio) {
    if (!piaoCard) return;
    let alerta = document.getElementById('alertaErroBaixaSorteio');
    if (!alerta) {
      alerta = document.createElement('div');
      alerta.id = 'alertaErroBaixaSorteio';
      alerta.className = 'alert alert-warning small fw-semibold py-2 px-3 mt-3 mb-0 text-start';
      alerta.setAttribute('role', 'alert');
      piaoCard.appendChild(alerta);
    }
    alerta.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1"></i> Atenção: não foi possível salvar no servidor a baixa de <strong>${escapeHtml(premio)}</strong> para <strong>${escapeHtml(ganhador)}</strong>. Verifique a conexão.`;
  }

  function getItemTotalWidth() {
    const primeiroItem = track ? track.querySelector('.item-participante') : null;
    if (primeiroItem) {
      const estilo = window.getComputedStyle(primeiroItem);
      const margemHorizontal =
        parseFloat(estilo.marginLeft || 0) + parseFloat(estilo.marginRight || 0);
      return primeiroItem.offsetWidth + margemHorizontal;
    }
    const isFS = Boolean(document.fullscreenElement || document.webkitFullscreenElement);
    return (isFS ? 540 : 230) + 20;
  }

  function getAudioContext() {
    if (!audioCtx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        audioCtx = new AudioCtx();
      }
    }
    return audioCtx;
  }

  function tocarTick() {
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      if (ctx.state === 'suspended') ctx.resume();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(520, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(140, ctx.currentTime + 0.028);
      gain.gain.setValueAtTime(0.11, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.028);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.028);
    } catch (_) {}
  }

  function tocarFanfarra() {
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      if (ctx.state === 'suspended') ctx.resume();
      const notas = [261.63, 329.63, 392.0, 523.25, 659.25];
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
    } catch (_) {}
  }

  function iniciarSincronizacaoSom() {
    if (rafSyncId) cancelAnimationFrame(rafSyncId);

    const itemTotalWidth = getItemTotalWidth();
    const wrapperWidth = wrapper ? wrapper.offsetWidth : 800;
    const centroWrapper = wrapperWidth / 2;
    let ultimoIndiceCruzado = -1;

    function verificarPassagem() {
      if (!estaRodando || !track) return;

      const transformStr = window.getComputedStyle(track).transform;
      if (transformStr && transformStr !== 'none') {
        const matriz = new DOMMatrix(transformStr);
        const currentX = matriz.m41;
        const indiceSobPonteiro = Math.floor(
          (centroWrapper - currentX) / itemTotalWidth
        );

        if (indiceSobPonteiro !== ultimoIndiceCruzado) {
          ultimoIndiceCruzado = indiceSobPonteiro;
          tocarTick();
        }
      }

      rafSyncId = requestAnimationFrame(verificarPassagem);
    }

    rafSyncId = requestAnimationFrame(verificarPassagem);
  }

  function pararSincronizacaoSom() {
    if (rafSyncId) {
      cancelAnimationFrame(rafSyncId);
      rafSyncId = null;
    }
  }

  function posicionarNoItem(index, comAnimacao = false) {
    if (!track) return;
    indiceAtual = index;
    const itemTotalWidth = getItemTotalWidth();
    const wrapperWidth = wrapper ? wrapper.offsetWidth : 800;
    const centroWrapper = wrapperWidth / 2;
    const offsetItem = index * itemTotalWidth + itemTotalWidth / 2;
    const targetX = centroWrapper - offsetItem;

    if (!comAnimacao) {
      track.style.transition = 'none';
    }
    track.style.transform = `translateX(${targetX}px)`;
  }

  function construirEsteira() {
    if (!track) return;
    track.innerHTML = '';

    if (participantes.length === 0) {
      track.innerHTML =
        '<div class="item-participante text-white opacity-50"><span>Sem participantes elegíveis</span></div>';
      posicionarNoItem(0);
      return;
    }

    const listaEsteira = [];
    const repeticoes = Math.max(15, Math.ceil(80 / participantes.length));
    for (let r = 0; r < repeticoes; r++) {
      participantes.forEach((nome) => listaEsteira.push(nome));
    }

    listaEsteira.forEach((nome, index) => {
      const div = document.createElement('div');
      div.className = 'item-participante';
      div.dataset.index = index;

      const span = document.createElement('span');
      span.textContent = nome;
      div.appendChild(span);

      track.appendChild(div);
    });

    posicionarNoItem(0);
  }

  function atualizarListasPremiosUI() {
    const contagem = {};
    poolPremios.forEach((nome) => {
      contagem[nome] = (contagem[nome] || 0) + 1;
    });

    const nomes = Object.keys(contagem);

    // 1. Lista da coluna lateral e badge do cabeçalho
    const listaEsquerda = document.getElementById('listaPremiosEsquerda');
    if (listaEsquerda) {
      const cardLateral = listaEsquerda.closest('.card');
      const badgeCabecalho = cardLateral ? cardLateral.querySelector('.card-header .badge') : null;
      if (badgeCabecalho) {
        badgeCabecalho.textContent = nomes.length;
      }

      listaEsquerda.innerHTML = '';
      if (nomes.length === 0) {
        listaEsquerda.innerHTML = `
          <li class="list-group-item text-muted px-0 py-4 text-center small border-0">
            <i class="bi bi-check-circle-fill fs-3 text-verde-escuro d-block opacity-75 mb-1"></i>
            Todos os prêmios foram sorteados!
          </li>`;
      } else {
        nomes.forEach((nome) => {
          const nomeSeguro = escapeHtml(nome);
          const li = document.createElement('li');
          li.className =
            'list-group-item d-flex justify-content-between align-items-center px-0 py-2';
          li.innerHTML = `
            <span class="fw-semibold text-dark">
              <i class="bi bi-gift-fill text-verde-escuro me-2"></i>${nomeSeguro}
            </span>
            <span class="badge badge-verde-suave border rounded-pill px-3 py-1">
              ${contagem[nome]} un.
            </span>`;
          listaEsquerda.appendChild(li);
        });
      }
    }

    // 2. Painel flutuante em tela cheia
    const floatPanel = document.querySelector('.fullscreen-prizes-panel');
    if (floatPanel) {
      const badgeTotal = floatPanel.querySelector('.badge.bg-warning');
      if (badgeTotal) badgeTotal.textContent = nomes.length;

      const floatPanelList = floatPanel.querySelector('ul');
      if (floatPanelList) {
        floatPanelList.innerHTML = '';
        if (nomes.length === 0) {
          floatPanelList.innerHTML =
            '<li class="text-white-50 py-2">Todos os prêmios foram sorteados!</li>';
        } else {
          nomes.forEach((nome) => {
            const nomeSeguro = escapeHtml(nome);
            const li = document.createElement('li');
            li.className = 'd-flex justify-content-between align-items-center py-1';
            li.innerHTML = `
              <span class="text-truncate text-white" style="max-width: 170px;" title="${nomeSeguro}">
                <i class="bi bi-gift me-1 text-warning"></i>${nomeSeguro}
              </span>
              <span class="badge bg-light text-dark fw-bold">${contagem[nome]} un.</span>`;
            floatPanelList.appendChild(li);
          });
        }
      }
    }
  }

  function adicionarAoHistorico(ganhador, premio) {
    if (msgVazio) msgVazio.style.display = 'none';
    if (listaHistorico) {
      const li = document.createElement('li');
      li.className =
        'list-group-item d-flex justify-content-between align-items-center px-0 py-3';
      li.innerHTML = `
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-warning text-dark rounded-pill px-2 py-1">
            <i class="bi bi-trophy-fill"></i>
          </span>
          <strong class="text-dark">${escapeHtml(ganhador)}</strong>
        </div>
        <span class="badge badge-verde-suave border rounded-pill px-3 py-1 fw-semibold">
          <i class="bi bi-gift-fill me-1"></i>${escapeHtml(premio)}
        </span>`;
      listaHistorico.insertBefore(li, listaHistorico.firstChild);
    }
  }

  function atualizarEstadoInicial() {
    if (totalParticipantesEl) {
      totalParticipantesEl.textContent = participantes.length;
    }

    if (participantesIniciais.length === 0 || poolPremios.length === 0) {
      if (btnSorteio) btnSorteio.disabled = true;
      if (
        statusText &&
        participantesIniciais.length === 0 &&
        poolPremios.length > 0
      ) {
        statusText.textContent = 'NENHUM PARTICIPANTE COM CHECK-IN';
      }
    }
  }

  function rodarPiaoHorizontal() {
    if (estaRodando || participantes.length === 0 || poolPremios.length === 0) {
      return;
    }

    participantes = embaralharArray(participantes);
    poolPremios = embaralharArray(poolPremios);
    construirEsteira();

    estaRodando = true;
    if (btnSorteio) btnSorteio.disabled = true;

    const indexPremioSorteado = randomInt(poolPremios.length);
    premioSorteadoAtual = poolPremios[indexPremioSorteado];

    clearInterval(intervalEmbaralharPremio);
    if (nomePremioAtualEl) {
      intervalEmbaralharPremio = setInterval(() => {
        if (poolPremios.length > 0) {
          const nomeTemp = poolPremios[randomInt(poolPremios.length)];
          nomePremioAtualEl.innerHTML = `<i class="bi bi-shuffle me-1"></i><span class="text-white">${escapeHtml(nomeTemp)}</span>`;
        }
      }, 80);
    }

    if (statusText) {
      statusText.textContent = 'SORTEANDO PARTICIPANTE E PRÊMIO...';
    }

    const antigoVencedor = track.querySelector('.vencedor');
    if (antigoVencedor) antigoVencedor.classList.remove('vencedor');

    const ganhadorIndexOriginal = randomInt(participantes.length);
    const ganhadorNome = participantes[ganhadorIndexOriginal];

    const repeticoesTotais = Math.max(15, Math.ceil(80 / participantes.length));
    const voltasAntesDaParada = Math.max(4, Math.floor(repeticoesTotais / 2));
    const targetIndexInTrack =
      participantes.length * voltasAntesDaParada + ganhadorIndexOriginal;

    posicionarNoItem(0, false);
    track.offsetHeight;

    track.style.transition =
      'transform 6s cubic-bezier(0.15, 0.90, 0.25, 1.00)';
    posicionarNoItem(targetIndexInTrack, true);

    iniciarSincronizacaoSom();

    clearTimeout(timerAnimacao);
    timerAnimacao = setTimeout(() => {
      pararSincronizacaoSom();
      clearInterval(intervalEmbaralharPremio);

      if (nomePremioAtualEl) {
        nomePremioAtualEl.innerHTML = `<i class="bi bi-gift-fill me-1"></i><span class="text-warning fw-bold">${escapeHtml(premioSorteadoAtual)}</span>`;
      }

      const itemElement = track.querySelector(
        `[data-index="${targetIndexInTrack}"]`
      );
      if (itemElement) itemElement.classList.add('vencedor');

      if (statusText) {
        statusText.innerHTML = `<i class="bi bi-trophy-fill text-warning me-2"></i>GANHADOR(A): ${escapeHtml(ganhadorNome.toUpperCase())}`;
      }

      tocarFanfarra();
      if (lancarConfetes) {
        lancarConfetes({
          particleCount: 130,
          spread: 85,
          origin: { y: 0.6 },
        });
      }

      const premioGanho = premioSorteadoAtual;

      // Remove participante da rodada atual e desconta o prêmio sorteado
      participantes.splice(ganhadorIndexOriginal, 1);
      poolPremios.splice(indexPremioSorteado, 1);

      if (totalParticipantesEl) {
        totalParticipantesEl.textContent = participantes.length;
      }
      atualizarListasPremiosUI();
      adicionarAoHistorico(ganhadorNome, premioGanho);

      // Registra baixa no Django
      fetch(resolverUrlBaixa(), {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
          ganhador_nome: ganhadorNome,
          premio_nome: premioGanho,
        }),
      })
        .then((res) => {
          if (!res.ok) {
            throw new Error(`HTTP ${res.status} ${res.statusText}`);
          }
        })
        .catch((err) => {
          console.error('Erro ao dar baixa no banco de dados:', err);
          notificarErroBaixa(ganhadorNome, premioGanho);
        });

      // Prepara próxima rodada após 2.5s
      clearTimeout(timerProximaRodada);
      timerProximaRodada = setTimeout(() => {
        if (poolPremios.length === 0) {
          construirEsteira();
          estaRodando = false;
          if (btnSorteio) btnSorteio.disabled = true;
          if (statusText) {
            statusText.textContent = 'TODOS OS PRÊMIOS FORAM SORTEADOS!';
          }
          return;
        }

        let elegiveisReiniciados = false;
        if (participantes.length === 0 && participantesIniciais.length > 0) {
          participantes = embaralharArray(participantesIniciais);
          elegiveisReiniciados = true;
          if (totalParticipantesEl) {
            totalParticipantesEl.textContent = participantes.length;
          }
        }

        construirEsteira();
        estaRodando = false;

        if (participantes.length === 0) {
          if (btnSorteio) btnSorteio.disabled = true;
          if (statusText) {
            statusText.textContent = 'NENHUM PARTICIPANTE ELEGÍVEL';
          }
        } else {
          if (btnSorteio) btnSorteio.disabled = false;
          if (statusText) {
            statusText.textContent = elegiveisReiniciados
              ? 'ELEGÍVEIS REINICIADOS! PRONTO PARA O PRÓXIMO SORTEIO!'
              : 'PRONTO PARA O PRÓXIMO SORTEIO!';
          }
        }
      }, 2500);
    }, 6000);
  }

  // Inicialização
  construirEsteira();
  atualizarListasPremiosUI();
  atualizarEstadoInicial();

  if (btnSorteio) {
    btnSorteio.addEventListener('click', rodarPiaoHorizontal);
  }

  if (btnFullscreen && piaoCard) {
    btnFullscreen.addEventListener('click', function () {
      const isFS = document.fullscreenElement || document.webkitFullscreenElement;
      if (!isFS) {
        const req = piaoCard.requestFullscreen || piaoCard.webkitRequestFullscreen;
        if (req) {
          Promise.resolve(req.call(piaoCard)).catch((err) =>
            alert(`Erro ao ativar tela cheia: ${err.message}`)
          );
        }
      } else {
        const exit = document.exitFullscreen || document.webkitExitFullscreen;
        if (exit) exit.call(document);
      }
    });
  }

  ['fullscreenchange', 'webkitfullscreenchange'].forEach((ev) => {
    document.addEventListener(ev, () => {
      if (!estaRodando) {
        requestAnimationFrame(() => posicionarNoItem(indiceAtual, false));
      }
    });
  });

  window.addEventListener('resize', () => {
    if (!estaRodando) {
      posicionarNoItem(indiceAtual, false);
    }
  });

  if (btnReiniciar) {
    btnReiniciar.addEventListener('click', () => {
      if (lancarConfetes && typeof lancarConfetes.reset === 'function') {
        lancarConfetes.reset();
      }
      window.location.replace(window.location.pathname + '?r=' + Date.now());
    });
  }

  window.addEventListener('pagehide', () => {
    pararSincronizacaoSom();
    clearInterval(intervalEmbaralharPremio);
    clearTimeout(timerAnimacao);
    clearTimeout(timerProximaRodada);
  });
});