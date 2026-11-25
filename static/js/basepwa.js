(function () {
  const KEYS = {
    MODO_ATIVO: 'pwa_modo_ativo',
    QUIOSQUE_URL: 'pwa_quiosque_url',
    FLUXO_PARTICIPANTE: 'pwa_fluxo_participante',
    SAIU_POR_PIN: 'pwa_saiu_por_pin',
  };

  const urlHome = document.documentElement.dataset.pwaHomeUrl || '/pwa_home/';
  const rotasParticipante = ['/boas-vindas/', '/quizzes/', '/desafio/'];

  // =========================================================
  // 1. API GLOBAL DO MODO QUIOSQUE (usada pelo leitor_qrcode.js)
  // =========================================================
  window.PwaKiosk = {
    KEYS,
    ativarModoQuiosque(url) {
      sessionStorage.removeItem(KEYS.FLUXO_PARTICIPANTE);
      sessionStorage.removeItem(KEYS.SAIU_POR_PIN);
      localStorage.removeItem(KEYS.QUIOSQUE_URL);
      sessionStorage.setItem(KEYS.QUIOSQUE_URL, url);
    },
    sairModoQuiosque() {
      localStorage.removeItem(KEYS.QUIOSQUE_URL);
      sessionStorage.removeItem(KEYS.QUIOSQUE_URL);
      sessionStorage.removeItem(KEYS.FLUXO_PARTICIPANTE);
      sessionStorage.setItem(KEYS.SAIU_POR_PIN, '1');
    },
    iniciarFluxoParticipante() {
      sessionStorage.setItem(KEYS.FLUXO_PARTICIPANTE, '1');
    },
    limparSessaoPwa() {
      sessionStorage.removeItem(KEYS.MODO_ATIVO);
      sessionStorage.removeItem(KEYS.SAIU_POR_PIN);
      sessionStorage.removeItem(KEYS.QUIOSQUE_URL);
    },
    limparSaidaPin() {
      sessionStorage.removeItem(KEYS.SAIU_POR_PIN);
    },
    registrarGatilhoToques(elemento, callback, totalToques = 5, janelaMs = 3000) {
      if (!elemento || typeof callback !== 'function') return;
      let contagem = 0;
      let timer = null;

      elemento.addEventListener('click', function () {
        contagem += 1;
        clearTimeout(timer);

        if (contagem >= totalToques) {
          contagem = 0;
          callback();
          return;
        }

        timer = setTimeout(function () {
          contagem = 0;
        }, janelaMs);
      });
    },
  };

  // =========================================================
  // 2. PROTEÇÃO DE NAVEGAÇÃO E HISTÓRICO (execução imediata)
  // =========================================================
  sessionStorage.setItem(KEYS.MODO_ATIVO, '1');
  localStorage.removeItem(KEYS.QUIOSQUE_URL);

  const params = new URLSearchParams(window.location.search);
  if (params.get('inicio') === '1') {
    sessionStorage.removeItem(KEYS.QUIOSQUE_URL);
    sessionStorage.removeItem(KEYS.FLUXO_PARTICIPANTE);
    sessionStorage.removeItem(KEYS.SAIU_POR_PIN);
    window.history.replaceState({ pwaGuard: true }, '', window.location.pathname);
  }

  function normalizarPath(urlOuPath) {
    return new URL(urlOuPath, window.location.origin).pathname.replace(/\/$/, '');
  }

  function ehRotaParticipante(pathname) {
    return rotasParticipante.some((rota) => pathname.includes(rota));
  }

  function foiNavegacaoVoltarAvancar(event) {
    if (event && event.persisted) return true;
    try {
      const navEntries = performance.getEntriesByType('navigation');
      if (navEntries && navEntries.length > 0) {
        return navEntries[0].type === 'back_forward';
      }
      if (performance.navigation) {
        return performance.navigation.type === 2;
      }
    } catch (_) {}
    return false;
  }

  function verificarNavegacao(event) {
    const pathAtual = window.location.pathname;
    const pathAtualNorm = pathAtual.replace(/\/$/, '');
    const pathHomeNorm = normalizarPath(urlHome);
    const trava = sessionStorage.getItem(KEYS.QUIOSQUE_URL);
    const naTelaParticipante = ehRotaParticipante(pathAtual);
    const ehBackForward = foiNavegacaoVoltarAvancar(event);

    if (naTelaParticipante && ehBackForward) {
      sessionStorage.removeItem(KEYS.FLUXO_PARTICIPANTE);
      window.location.replace(trava || urlHome);
      return;
    }

    if (pathAtual.includes('/boas-vindas/') && !ehBackForward) {
      sessionStorage.setItem(KEYS.FLUXO_PARTICIPANTE, '1');
    }

    if (!naTelaParticipante) {
      sessionStorage.removeItem(KEYS.FLUXO_PARTICIPANTE);
    }

    if (trava) {
      try {
        const pathTravaNorm = normalizarPath(trava);
        const fluxoAtivo = sessionStorage.getItem(KEYS.FLUXO_PARTICIPANTE) === '1';

        if (naTelaParticipante && !fluxoAtivo) {
          window.location.replace(trava);
          return;
        }

        if (pathAtualNorm !== pathTravaNorm && !naTelaParticipante) {
          window.location.replace(trava);
          return;
        }
      } catch (_) {
        sessionStorage.removeItem(KEYS.QUIOSQUE_URL);
      }
      return;
    }

    if (naTelaParticipante) {
      window.location.replace(urlHome);
      return;
    }

    if (sessionStorage.getItem(KEYS.SAIU_POR_PIN) === '1' && pathAtualNorm !== pathHomeNorm) {
      window.location.replace(urlHome);
    }
  }

  if ('navigation' in window && window.navigation) {
    window.navigation.addEventListener('navigate', function (event) {
      if (event.navigationType !== 'traverse') return;

      const pathAtual = window.location.pathname;
      const pathAtualNorm = pathAtual.replace(/\/$/, '');
      const pathHomeNorm = normalizarPath(urlHome);
      const trava = sessionStorage.getItem(KEYS.QUIOSQUE_URL);

      if (ehRotaParticipante(pathAtual)) {
        sessionStorage.removeItem(KEYS.FLUXO_PARTICIPANTE);
        window.location.replace(trava || urlHome);
      } else if (trava) {
        window.location.replace(trava);
      } else if (pathAtualNorm !== pathHomeNorm) {
        window.location.replace(urlHome);
      }
    });
  }

  function protegerHistorico() {
    const pathAtual = window.location.pathname;
    if (ehRotaParticipante(pathAtual)) return;

    const pathAtualNorm = pathAtual.replace(/\/$/, '');
    const pathHomeNorm = normalizarPath(urlHome);

    function fixarEstado() {
      if (!window.history.state || !window.history.state.pwaGuard) {
        window.history.pushState({ pwaGuard: true }, '', window.location.href);
      }
    }

    fixarEstado();
    ['pointerdown', 'touchstart', 'keydown'].forEach(function (ev) {
      window.addEventListener(ev, fixarEstado, { once: true, passive: true });
    });

    window.addEventListener('popstate', function () {
      const trava = sessionStorage.getItem(KEYS.QUIOSQUE_URL);
      if (trava) {
        window.history.pushState({ pwaGuard: true }, '', trava);
      } else if (pathAtualNorm === pathHomeNorm) {
        window.history.pushState({ pwaGuard: true }, '', window.location.href);
      } else {
        window.location.replace(urlHome);
      }
    });
  }

  verificarNavegacao();
  protegerHistorico();

  window.addEventListener('pageshow', function (event) {
    sessionStorage.setItem(KEYS.MODO_ATIVO, '1');
    verificarNavegacao(event);

    if (event.persisted && document.body && document.body.dataset.reloadBfcache === 'true') {
      window.location.reload();
    }
  });

  // =========================================================
  // 3. COMPORTAMENTOS GLOBAIS DA INTERFACE (após DOM carregar)
  // =========================================================
  document.addEventListener('DOMContentLoaded', function () {
    const kiosk = window.PwaKiosk;
    const bodyData = document.body.dataset;

    // Barra superior secreta (5 toques recarregam o PWA)
    const safeBar = document.getElementById('pwaSafeBarReset');
    if (safeBar) {
      kiosk.registrarGatilhoToques(safeBar, () => window.location.reload(), 5, 2500);
    }

    // Links internos usando location.replace() para não empilhar histórico
    document.addEventListener('click', function (event) {
      const link = event.target.closest('a[href]');
      if (!link) return;

      const href = link.getAttribute('href');
      const isModifier = event.ctrlKey || event.metaKey || event.shiftKey || event.altKey;

      if (
        link.target === '_blank' ||
        link.hasAttribute('data-no-replace') ||
        isModifier ||
        !href ||
        href.startsWith('#') ||
        link.origin !== window.location.origin
      ) {
        return;
      }

      event.preventDefault();

      if (link.hasAttribute('data-pwa-exit')) {
        kiosk.limparSessaoPwa();
      }

      window.location.replace(link.href);
    });

    // Formulários que limpam a trava de saída por PIN ao enviar
    document.querySelectorAll('form[data-pwa-clear-pin]').forEach(function (form) {
      form.addEventListener('submit', function () {
        kiosk.limparSaidaPin();
      });
    });

    // Inputs com conversão automática para maiúsculas
    document.querySelectorAll('input[data-uppercase]').forEach(function (input) {
      input.addEventListener('input', function () {
        const inicio = input.selectionStart;
        const fim = input.selectionEnd;
        input.value = input.value.toUpperCase();
        if (typeof inicio === 'number' && typeof fim === 'number') {
          input.setSelectionRange(inicio, fim);
        }
      });
    });

    // Timers de retorno automático ao leitor (boas_vindas, quizzes, quiz_detail)
    const leitorUrl = bodyData.leitorUrl;
    const timeoutTotal = Number(bodyData.timeoutTotal || 0);
    const timeoutInatividade = Number(bodyData.timeoutInatividade || 0);
    const contadorId = bodyData.contadorId;

    if (leitorUrl) {
      const voltarParaLeitor = () => window.location.replace(leitorUrl);

      if (contadorId && timeoutTotal > 0) {
        const contadorEl = document.getElementById(contadorId);
        let restantes = timeoutTotal;

        const intervalo = setInterval(function () {
          restantes -= 1;
          if (contadorEl && restantes >= 0) {
            contadorEl.textContent = String(restantes);
          }
          if (restantes <= 0) {
            clearInterval(intervalo);
            voltarParaLeitor();
          }
        }, 1000);
      } else {
        if (timeoutTotal > 0) {
          setTimeout(voltarParaLeitor, timeoutTotal * 1000);
        }

        if (timeoutInatividade > 0) {
          let timerInatividade = setTimeout(voltarParaLeitor, timeoutInatividade * 1000);
          ['pointerdown', 'touchstart', 'scroll', 'keydown', 'input'].forEach(function (ev) {
            document.addEventListener(
              ev,
              function () {
                clearTimeout(timerInatividade);
                timerInatividade = setTimeout(voltarParaLeitor, timeoutInatividade * 1000);
              },
              { passive: true }
            );
          });
        }
      }
    }
  });
})();