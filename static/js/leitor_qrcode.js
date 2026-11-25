document.addEventListener('DOMContentLoaded', function () {
  const LOCK_KEY = 'pwa_quiosque_url';
  const PIN_EXIT_KEY = 'pwa_saiu_por_pin';
  const PARTICIPANT_FLOW_KEY = 'pwa_fluxo_participante';
  const MAX_TENTATIVAS_CAMERA = 3;
  const TIMEOUT_REQUISICAO_MS = 10000;

  const cfg = window.ConfigAtividade || {};
  const kiosk = window.PwaKiosk || null;
  const readerEl = document.getElementById('reader');
  const resultadoDiv = document.getElementById('resultado');

  const urlAtualLimpa = window.location.origin + window.location.pathname;

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

  const pinConfigurado = String(
    cfg.codigoLeitor ||
    readerEl?.dataset?.codigoLeitor ||
    codigoDaUrl
  )
    .trim()
    .toUpperCase();

  const urlSaidaQuiosque =
    cfg.urlSaidaStaff ||
    readerEl?.dataset?.urlSaida ||
    '/pwa_home/';

  const facingMode =
    cfg.facingMode ||
    readerEl?.dataset?.facingMode ||
    'user';

  let html5QrCode = null;
  let cameraAtiva = false;
  let cameraIniciando = false;
  let processandoLeitura = false;
  let saindoPeloPin = false;
  let tentativasCamera = 0;
  let timerRecuperacao = null;
  let timerReset = null;
  let audioCtx = null;

  function escapeHtml(texto) {
    return String(texto ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // =========================================================
  // 1. TRAVA DO MODO QUIOSQUE E BOTÃO VOLTAR
  // =========================================================
  if (kiosk) {
    kiosk.ativarModoQuiosque(urlAtualLimpa);
  } else {
    sessionStorage.removeItem(PARTICIPANT_FLOW_KEY);
    sessionStorage.removeItem(PIN_EXIT_KEY);
    localStorage.removeItem(LOCK_KEY);
    sessionStorage.setItem(LOCK_KEY, urlAtualLimpa);
  }

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
      if (!audioCtx) {
        audioCtx = new AudioCtx();
      }
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.12);
    } catch (_) {}
  }

  function exibirMensagem(tipoClasse, htmlConteudo) {
    if (!resultadoDiv) return;
    resultadoDiv.className = `resultado-box alert ${tipoClasse} border-0 shadow-sm mb-0`;
    resultadoDiv.innerHTML = htmlConteudo;
  }

  function resetarLeitor(atrasoMs = 3000) {
    clearTimeout(timerReset);
    timerReset = setTimeout(function () {
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
      html5QrCode = null;
    }

    if (readerEl) {
      readerEl.querySelectorAll('video').forEach(function (video) {
        if (video.srcObject) {
          video.srcObject.getTracks().forEach(function (track) {
            track.stop();
          });
          video.srcObject = null;
        }
      });
    }

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
    readerEl.classList.toggle('camera-frontal', facingMode === 'user');

    try {
      if (!html5QrCode) {
        html5QrCode = new Html5Qrcode('reader');
      }

      const larguraBox = Math.min(250, Math.floor((readerEl.clientWidth || 300) * 0.72));

      await html5QrCode.start(
        { facingMode },
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
    clearTimeout(timerReset);
    tocarBipConfirmacao();

    exibirMensagem(
      'alert-info',
      '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Validando crachá...'
    );

    await validarNoServidor(codigoLido);
  }

  async function validarNoServidor(codigoLido) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_REQUISICAO_MS);

    try {
      const response = await fetch(urlIdentificar, {
        method: 'POST',
        credentials: 'same-origin',
        signal: controller.signal,
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
        const msgSegura = escapeHtml(dados.mensagem || 'Acesso autorizado!');
        exibirMensagem(
          'alert-success',
          `<span><i class="bi bi-check-circle-fill me-1"></i> ${msgSegura}</span>`
        );

        if (dados.redirect_url) {
          saindoPeloPin = true;
          clearTimeout(timerRecuperacao);
          clearTimeout(timerReset);
          if (kiosk) {
            kiosk.iniciarFluxoParticipante();
          } else {
            sessionStorage.setItem(PARTICIPANT_FLOW_KEY, '1');
          }
          await pararCameraSeAtiva();
          window.location.replace(dados.redirect_url);
        } else {
          resetarLeitor(3000);
        }
      } else {
        const msgErroSegura = escapeHtml(dados?.mensagem || 'Acesso não autorizado.');
        exibirMensagem(
          'alert-danger',
          `<span><i class="bi bi-x-circle-fill me-1"></i> ${msgErroSegura}</span>`
        );
        resetarLeitor(3500);
      }
    } catch (erro) {
      console.error('Erro na requisição de identificação:', erro);
      const msgRede = erro?.name === 'AbortError'
        ? 'Tempo limite excedido ao validar crachá. Tente novamente.'
        : 'Falha de comunicação com o servidor. Tente novamente.';
      exibirMensagem(
        'alert-danger',
        `<span><i class="bi bi-wifi-off me-1"></i> ${msgRede}</span>`
      );
      resetarLeitor(3500);
    } finally {
      clearTimeout(timeoutId);
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
  // 6. GATILHO DOS 5 CLIQUES (#kioskSecretTrigger)
  // =========================================================
  const modalPinEl = document.getElementById('modalSaidaQuiosque');
  const formPinSaida = document.getElementById('formPinSaida');
  const inputPinSaida = document.getElementById('inputPinSaida');
  const erroPinSaida = document.getElementById('erroPinSaida');
  const secretTrigger = document.getElementById('kioskSecretTrigger');

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

  if (secretTrigger) {
    if (kiosk) {
      kiosk.registrarGatilhoToques(secretTrigger, abrirModalPin, 5, 3000);
    } else {
      let cliquesSecretos = 0;
      let timerCliques = null;
      secretTrigger.style.userSelect = 'none';
      secretTrigger.style.cursor = 'pointer';

      secretTrigger.addEventListener('click', function () {
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
    }
  }

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
        if (kiosk) {
          kiosk.sairModoQuiosque();
        } else {
          localStorage.removeItem(LOCK_KEY);
          sessionStorage.removeItem(LOCK_KEY);
          sessionStorage.removeItem(PARTICIPANT_FLOW_KEY);
          sessionStorage.setItem(PIN_EXIT_KEY, '1');
        }
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
    clearTimeout(timerReset);
    pararCameraSeAtiva();
  });

  iniciarCamera();
});