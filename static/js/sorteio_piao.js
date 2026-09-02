document.addEventListener('DOMContentLoaded', function () {
  let participantes = window.participantesData || [
    "Ana Silva", "Carlos Eduardo", "Beatriz Santos", "João Pereira", 
    "Mariana Costa", "Lucas Ferreira", "Fernanda Lima", "Rodrigo Alves"
  ];

  const btnSorteio = document.getElementById('btnSorteio');
  const btnFullscreen = document.getElementById('btnFullscreen');
  const btnReiniciar = document.getElementById('btnReiniciar');
  const statusText = document.getElementById('statusText');
  const piaoCard = document.getElementById('piaoCard');
  const piaoContainer = document.getElementById('piaoContainer');
  const track = document.getElementById('horizontalTrack');
  const wrapper = document.getElementById('horizontalWrapper');
  const listaHistorico = document.getElementById('listaHistorico');
  const msgVazio = document.getElementById('msgVazio');
  const totalParticipantesEl = document.getElementById('totalParticipantes');

  let estaRodando = false;
  let contadorSorteios = 0;

  function getItemTotalWidth() {
    const isFS = document.fullscreenElement !== null;
    const itemWidth = isFS ? 360 : 280;
    const itemMargin = 20; 
    return itemWidth + itemMargin;
  }

  if (totalParticipantesEl) {
    totalParticipantesEl.innerText = participantes.length;
  }

  // Efeitos Sonoros Simples via Web Audio API
  let audioCtx;
  function getAudioContext() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    return audioCtx;
  }

  function tocarTick() {
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
  }

  function tocarFanfarra() {
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
  }

  // Montagem da Esteira
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

  // Animação de Giro
  function rodarPiaoHorizontal() {
    if (estaRodando) return;
    if (participantes.length === 0) {
      alert("Todos os participantes já foram sorteados!");
      return;
    }

    estaRodando = true;
    if (btnSorteio) btnSorteio.disabled = true;
    if (statusText) statusText.innerText = "Sorteando participante...";

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
        finalizarSorteio(ganhadorIndexOriginal, targetIndex);
      }
    }

    requestAnimationFrame(animar);
  }

  function finalizarSorteio(originalIndex, targetIndex) {
    const ganhador = participantes[originalIndex];
    
    const cardSorteado = track.children[targetIndex];
    if (cardSorteado) cardSorteado.classList.add('vencedor');

    participantes.splice(originalIndex, 1);
    if (totalParticipantesEl) totalParticipantesEl.innerText = participantes.length;

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
          <i class="bi bi-trophy-fill text-success fs-4 me-3"></i>
          <div>
            <strong class="text-dark d-block fs-5">${ganhador}</strong>
            <small class="text-muted">Ganhador(a) do Sorteio</small>
          </div>
        </div>
        <span class="badge bg-success border px-3 py-2">${contadorSorteios}º Sorteio</span>
      `;
      listaHistorico.prepend(itemLista);
    }
  }

  // Tela Cheia
  if (btnFullscreen) {
    btnFullscreen.addEventListener('click', function () {
      if (!document.fullscreenElement) {
        piaoContainer.requestFullscreen().catch(err => {
          alert(`Erro ao ativar tela cheia: ${err.message}`);
        });
      } else {
        document.exitFullscreen();
      }
    });
  }

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