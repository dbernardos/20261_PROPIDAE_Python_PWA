document.addEventListener('DOMContentLoaded', function () {
  const LOCK_KEY = 'pwa_quiosque_url';
  const PIN_EXIT_KEY = 'pwa_saiu_por_pin';
  const PARTICIPANT_FLOW_KEY = 'pwa_fluxo_participante';
  const MAX_TENTATIVAS_CAMERA = 3;

  const cfg = window.ConfigAtividade || {};
  const readerEl = document.getElementById('reader');
  const resultadoDiv = document.getElementById('resultado');

  // URL limpa (sem ?csrfmiddlewaretoken ou ?cache-bust)
  const urlAtualLimpa = window.location.origin + window.location.pathname;

  // Fallback do código da atividade pela URL (ex: 52B-RQA)
  const partesUrl = window.location.pathname.split('/').filter(Boolean);
  const codigoDaUrl = partesUrl.length ? partesUrl[partesUrl.length - 1] : '';

  const urlIdentificar =
    cfg.urlIdentificar ||
    readerEl?.dataset?.urlIdentificar ||
    '/quiz/identificar/';

  const atividadeId =
    cfg.idAtividadeParaEnvio ||
    readerEl?.dataset?.atividadeId ||
    codigoDaUrl;

  // PIN = código do leitor da atividade (sempre em maiúsculas)
  const pinConfigurado = String(
    cfg.codigoLeitor ||
    readerEl?.dataset?.codigoLeitor ||
    codigoDaUrl
  )
    .trim()
    .toUpperCase();

  // Destino ao sair pelo PIN (pwa_home definido em ConfigAtividade.urlSaidaStaff)
  const urlSaidaQuiosque =
    cfg.urlSaidaStaff ||
    readerEl?.dataset?.urlSaida ||
    '/pwa_home/';

  let html5QrCode = null;
  let cameraAtiva = false;
  let cameraIniciando = false;
  let processandoLeitura = false;
  let saindoPeloPin = false;
  let tentativasCamera = 0;
  let timerRecuperacao = null;

  // =========================================================
  // 1. TRAVA DO MODO QUIOSQUE E BOTÃO VOLTAR
  // =========================================================
  sessionStorage.removeItem(PARTICIPANT_FLOW_KEY);
  sessionStorage.removeItem(PIN_EXIT_KEY);
  localStorage.setItem(LOCK_KEY, urlAtualLimpa);

  window.history.pushState({ pwaKiosk: true }, '', urlAtualLimpa);
  window.addEventListener('popstate', function () {
    if (!saindoPeloPin) {
      window.history.pushState({ pwaKiosk: true }, '', urlAtualLimpa);
    }
  });

  // =========================================================
  // 2. TOKEN CSRF
  // =========================================================
  function obterCsrfToken() {
    if (cfg.csrfToken) return cfg.csrfToken;
    const inputToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (inputToken && inputToken.value) return inputToken.value;
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  // =========================================================
  // 3. FEEDBACK SONORO E VISUAL
  // =========================================================
  function tocarBipConfirmacao() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, ctx.currentTime);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.12);
    } catch (_) {}
  }

  function exibirMensagem(tipoClasse, htmlConteudo) {
    if (!resultadoDiv) return;
    resultadoDiv.className = `resultado-box alert ${tipoClasse} border-0 shadow-sm mb-0`;
    resultadoDiv.innerHTML = htmlConteudo;
  }

  function resetarLeitor(atrasoMs = 3000) {
    setTimeout(function () {
      if (saindoPeloPin) return;
      processandoLeitura = false;
      if (resultadoDiv) {
        resultadoDiv.className = 'resultado-box';
        resultadoDiv.innerHTML = '';
      }
    }, atrasoMs);
  }

  // =========================================================
  // 4. CONTROLE DA CÂMERA
  // =========================================================
  async function pararCameraSeAtiva() {
    cameraIniciando = false;
    clearTimeout(timerRecuperacao);

    if (html5QrCode) {
      try {
        if (html5QrCode.isScanning) {
          await html5QrCode.stop();
        }
        await html5QrCode.clear();
      } catch (_) {}
    }

    document.querySelectorAll('video').forEach(function (video) {
      if (video.srcObject) {
        video.srcObject.getTracks().forEach(function (track) {
          track.stop();
        });
        video.srcObject = null;
      }
    });

    cameraAtiva = false;
  }

  async function iniciarCamera() {
    if (!readerEl || cameraAtiva || cameraIniciando || saindoPeloPin || document.hidden) {
      return;
    }

    if (typeof Html5Qrcode === 'undefined') {
      exibirMensagem(
        'alert-danger',
        '<span><i class="bi bi-exclamation-triangle-fill me-1"></i> Biblioteca do leitor não carregada.</span>'
      );
      return;
    }

    cameraIniciando = true;

    try {
      if (!html5QrCode) {
        html5QrCode = new Html5Qrcode('reader');
      }

      const larguraBox = Math.min(250, Math.floor((readerEl.clientWidth || 300) * 0.72));

      await html5QrCode.start(
        { facingMode: 'user' },
        {
          fps: 10,
          qrbox: { width: larguraBox, height: larguraBox },
          aspectRatio: 1.0,
        },
        onScanSuccess,
        function () {}
      );

      cameraAtiva = true;
      cameraIniciando = false;
      tentativasCamera = 0;
      agendarVerificacaoVideo();
    } catch (err) {
      cameraAtiva = false;
      cameraIniciando = false;
      const erroStr = String(err || '');

      if (
        (erroStr.includes('NotReadableError') ||
          erroStr.includes('Device in use') ||
          erroStr.includes('AbortError')) &&
        tentativasCamera < MAX_TENTATIVAS_CAMERA
      ) {
        tentativasCamera += 1;
        await pararCameraSeAtiva();
        setTimeout(iniciarCamera, 800);
        return;
      }

      console.error('Erro ao iniciar câmera:', err);
      exibirMensagem(
        'alert-warning',
        '<span><i class="bi bi-camera-video-off me-1"></i> Não foi possível acessar a câmera. Use o campo manual abaixo.</span>'
      );
    }
  }

  function agendarVerificacaoVideo() {
    clearTimeout(timerRecuperacao);
    timerRecuperacao = setTimeout(async function () {
      if (saindoPeloPin || document.hidden) return;
      const video = readerEl ? readerEl.querySelector('video') : null;
      if (!video || video.readyState === 0) {
        await pararCameraSeAtiva();
        iniciarCamera();
      }
    }, 3500);
  }

  // =========================================================
  // 5. VALIDAÇÃO NO SERVIDOR (QR CODE E CÓDIGO MANUAL)
  // =========================================================
  async function onScanSuccess(decodedText) {
    if (processandoLeitura || saindoPeloPin) return;

    const codigoLido = String(decodedText || '').trim();
    if (!codigoLido) return;

    processandoLeitura = true;
    tocarBipConfirmacao();

    exibirMensagem(
      'alert-info',
      '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Validando crachá...'
    );

    await validarNoServidor(codigoLido);
  }

  async function validarNoServidor(codigoLido) {
    try {
      const response = await fetch(urlIdentificar, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': obterCsrfToken(),
        },
        body: JSON.stringify({
          codigo: codigoLido,
          atividade_id: atividadeId,
        }),
      });

      if (response.status === 403) {
        saindoPeloPin = true;
        await pararCameraSeAtiva();
        window.location.replace(urlAtualLimpa);
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}`);
      }

      const dados = await response.json();

      if (dados && dados.autorizado) {
        exibirMensagem(
          'alert-success',
          `<span><i class="bi bi-check-circle-fill me-1"></i> ${dados.mensagem}</span>`
        );

        if (dados.redirect_url) {
          saindoPeloPin = true;
          clearTimeout(timerRecuperacao);
          sessionStorage.setItem(PARTICIPANT_FLOW_KEY, '1');
          await pararCameraSeAtiva();
          window.location.replace(dados.redirect_url);
        } else {
          resetarLeitor(3000);
        }
      } else {
        exibirMensagem(
          'alert-danger',
          `<span><i class="bi bi-x-circle-fill me-1"></i> ${dados?.mensagem || 'Acesso não autorizado.'}</span>`
        );
        resetarLeitor(3500);
      }
    } catch (erro) {
      console.error('Erro na requisição de identificação:', erro);
      exibirMensagem(
        'alert-danger',
        '<span><i class="bi bi-wifi-off me-1"></i> Falha de comunicação com o servidor. Tente novamente.</span>'
      );
      resetarLeitor(3500);
    }
  }

  // Formulário de código manual (#formManual)
  const formManual = document.getElementById('formManual');
  const inputManual = document.getElementById('codigoManual');

  if (formManual) {
    formManual.addEventListener('submit', function (e) {
      e.preventDefault();
      const codigo = (inputManual ? inputManual.value : '').trim();
      if (!codigo) return;
      if (inputManual) inputManual.value = '';
      onScanSuccess(codigo);
    });
  }

  // =========================================================
  // 6. GATILHO DOS 5 CLIQUES (#kioskSecretTrigger e título)
  // =========================================================
  const modalPinEl = document.getElementById('modalSaidaQuiosque');
  const formPinSaida = document.getElementById('formPinSaida');
  const inputPinSaida = document.getElementById('inputPinSaida');
  const erroPinSaida = document.getElementById('erroPinSaida');

  const triggers = [
    document.getElementById('kioskSecretTrigger'),
    document.querySelector('.cabecalho-pwa h2'),
  ].filter(Boolean);

  let cliquesSecretos = 0;
  let timerCliques = null;

  function abrirModalPin() {
    if (!modalPinEl) return;

    if (erroPinSaida) erroPinSaida.classList.add('d-none');
    if (inputPinSaida) {
      inputPinSaida.value = '';
      inputPinSaida.classList.remove('is-invalid');
    }

    if (window.bootstrap && window.bootstrap.Modal) {
      window.bootstrap.Modal.getOrCreateInstance(modalPinEl).show();
    } else {
      modalPinEl.classList.add('show');
      modalPinEl.style.display = 'block';
    }

    setTimeout(function () {
      if (inputPinSaida) inputPinSaida.focus();
    }, 300);
  }

  triggers.forEach(function (el) {
    el.style.userSelect = 'none';
    el.style.cursor = 'pointer';

    el.addEventListener('click', function () {
      cliquesSecretos += 1;
      clearTimeout(timerCliques);

      if (cliquesSecretos >= 5) {
        cliquesSecretos = 0;
        abrirModalPin();
        return;
      }

      timerCliques = setTimeout(function () {
        cliquesSecretos = 0;
      }, 3000);
    });
  });

  // =========================================================
  // 7. VALIDAÇÃO DO PIN (CÓDIGO DA ATIVIDADE) E SAÍDA
  // =========================================================
  if (formPinSaida) {
    formPinSaida.addEventListener('submit', async function (e) {
      e.preventDefault();
      const valorDigitado = (inputPinSaida ? inputPinSaida.value : '').trim().toUpperCase();

      if (!valorDigitado) return;

      if (valorDigitado === pinConfigurado) {
        saindoPeloPin = true;
        localStorage.removeItem(LOCK_KEY);
        sessionStorage.removeItem(PARTICIPANT_FLOW_KEY);
        sessionStorage.setItem(PIN_EXIT_KEY, '1');
        await pararCameraSeAtiva();
        window.location.replace(urlSaidaQuiosque);
      } else {
        if (erroPinSaida) {
          erroPinSaida.textContent = 'Código da atividade incorreto.';
          erroPinSaida.classList.remove('d-none');
        }
        if (inputPinSaida) {
          inputPinSaida.classList.add('is-invalid');
          inputPinSaida.value = '';
          inputPinSaida.focus();
        }
      }
    });
  }

  // =========================================================
  // 8. CICLO DE VIDA DA PÁGINA
  // =========================================================
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
      pararCameraSeAtiva();
    } else if (!saindoPeloPin) {
      setTimeout(iniciarCamera, 450);
    }
  });

  window.addEventListener('pageshow', function (event) {
    if (event.persisted && !saindoPeloPin) {
      pararCameraSeAtiva().then(function () {
        setTimeout(iniciarCamera, 450);
      });
    }
  });

  window.addEventListener('pagehide', function () {
    pararCameraSeAtiva();
  });

  // Inicialização
  iniciarCamera();
});