document.addEventListener('DOMContentLoaded', () => {
  // 1. Controle de inatividade da sessão (apenas se os atributos existirem no body)
  const { sessionTimeout, loginUrl } = document.body.dataset;
  const segundosLimite = Number(sessionTimeout);
  const tempoLimite = Number.isFinite(segundosLimite) && segundosLimite > 0
    ? Math.min(segundosLimite * 1000, 2147483647)
    : 0;

  if (tempoLimite > 0 && loginUrl) {
    const STORAGE_KEY_ATIVIDADE = 'sea_ultima_atividade_ts';
    let timerSessao = null;
    let sessaoExpirada = false;
    let ultimaGravacaoStorage = 0;

    const encerrarPorInatividade = () => {
      if (sessaoExpirada) return;
      sessaoExpirada = true;
      clearTimeout(timerSessao);
      alert('Sua sessão expirou após inatividade. Faça login novamente.');
      const separador = loginUrl.includes('?') ? '&' : '?';
      window.location.replace(`${loginUrl}${separador}expirado=1&t=${Date.now()}`);
    };

    const agendarExpiracao = (restanteMs = tempoLimite) => {
      clearTimeout(timerSessao);
      if (restanteMs <= 0) {
        encerrarPorInatividade();
        return;
      }
      timerSessao = setTimeout(encerrarPorInatividade, restanteMs);
    };

    const registrarAtividade = () => {
      if (sessaoExpirada) return;
      const agora = Date.now();
      agendarExpiracao(tempoLimite);

      if (agora - ultimaGravacaoStorage > 5000) {
        ultimaGravacaoStorage = agora;
        try {
          localStorage.setItem(STORAGE_KEY_ATIVIDADE, String(agora));
        } catch (_) {}
      }
    };

    ['mousemove', 'keydown', 'click', 'touchstart', 'scroll'].forEach((ev) => {
      window.addEventListener(ev, registrarAtividade, { passive: true });
    });

    window.addEventListener('storage', (e) => {
      if (e.key === STORAGE_KEY_ATIVIDADE && e.newValue) {
        const ts = Number(e.newValue);
        if (Number.isFinite(ts)) {
          const restante = tempoLimite - (Date.now() - ts);
          agendarExpiracao(restante);
        }
      }
    });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) return;
      try {
        const ts = Number(localStorage.getItem(STORAGE_KEY_ATIVIDADE));
        if (Number.isFinite(ts) && ts > 0) {
          const restante = tempoLimite - (Date.now() - ts);
          if (restante <= 0) {
            encerrarPorInatividade();
            return;
          }
          agendarExpiracao(restante);
        }
      } catch (_) {}
    });

    registrarAtividade();
  }

  // 2. Marca labels de campos obrigatórios
  document.querySelectorAll('input[required], select[required], textarea[required]').forEach((input) => {
    if (!input.id) return;
    const label = document.querySelector(`label[for="${input.id}"]`);
    if (label) {
      label.classList.add('required');
    }
  });

  // 3. Botão de mostrar/ocultar senha
  document.querySelectorAll('input[type="password"]').forEach((input) => {
    if (input.parentElement && input.parentElement.classList.contains('input-group')) return;

    const group = document.createElement('div');
    group.className = 'input-group has-validation';
    input.parentNode.insertBefore(group, input);
    group.appendChild(input);

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-outline-secondary';
    btn.setAttribute('aria-label', 'Mostrar ou ocultar senha');
    btn.setAttribute('aria-pressed', 'false');
    btn.innerHTML = '<i class="bi bi-eye" aria-hidden="true"></i>';

    btn.addEventListener('click', () => {
      const oculto = input.type === 'password';
      input.type = oculto ? 'text' : 'password';
      btn.setAttribute('aria-pressed', String(oculto));
      btn.innerHTML = `<i class="bi bi-eye${oculto ? '-slash' : ''}" aria-hidden="true"></i>`;
    });

    group.appendChild(btn);
  });

  // 4. Máscara de CPF: 000.000.000-00
  const formatarCpf = (valor) => {
    let v = String(valor || '').replace(/\D/g, '').slice(0, 11);
    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    return v;
  };

  document.querySelectorAll('input[name$="cpf"]').forEach((input) => {
    input.maxLength = 14;
    if (!input.inputMode) input.inputMode = 'numeric';
    if (input.value) input.value = formatarCpf(input.value);

    input.addEventListener('input', (e) => {
      e.target.value = formatarCpf(e.target.value);
    });
  });

  // 5. Máscara de Telefone: (00) 00000-0000 ou (00) 0000-0000
  const formatarTelefone = (valor) => {
    let v = String(valor || '').replace(/\D/g, '').slice(0, 11);
    if (v.length > 10) {
      return v.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
    }
    if (v.length > 6) {
      return v.replace(/^(\d{2})(\d{4})(\d{0,4}).*/, '($1) $2-$3');
    }
    if (v.length > 2) {
      return v.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
    }
    if (v.length > 0) {
      return v.replace(/^(\d*)/, '($1');
    }
    return '';
  };

  document.querySelectorAll('input[name$="telefone"]').forEach((input) => {
    input.maxLength = 15;
    if (!input.inputMode) input.inputMode = 'numeric';
    if (input.value) input.value = formatarTelefone(input.value);

    input.addEventListener('input', (e) => {
      e.target.value = formatarTelefone(e.target.value);
    });
  });
});