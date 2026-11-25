/* ==========================================================================
   GERENCIADOR DE MINHAS INSCRIÇÕES
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const inicializarTooltips = () => {
    if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip) return;
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
      bootstrap.Tooltip.getOrCreateInstance(el);
    });
  };

  const restaurarBotoesCancelamento = () => {
    document.querySelectorAll('.form-cancelar-atividade button[type="submit"]').forEach((btn) => {
      if (btn.dataset.originalHtml) {
        btn.disabled = false;
        btn.innerHTML = btn.dataset.originalHtml;
      }
    });
  };

  const configurarEventos = () => {
    document.querySelectorAll('.form-cancelar-atividade').forEach((form) => {
      form.addEventListener('submit', (e) => {
        if (!window.confirm('Deseja realmente cancelar sua participação nesta atividade?')) {
          e.preventDefault();
          return;
        }

        const btn = form.querySelector('button[type="submit"]');
        if (btn) {
          if (!btn.dataset.originalHtml) {
            btn.dataset.originalHtml = btn.innerHTML;
          }
          btn.disabled = true;
          btn.innerHTML =
            '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Cancelando...';
        }
      });
    });

    document.querySelectorAll('.btn-imprimir-cracha').forEach((btn) => {
      btn.addEventListener('click', () => window.print());
    });
  };

  window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
      restaurarBotoesCancelamento();
    }
  });

  inicializarTooltips();
  configurarEventos();
});