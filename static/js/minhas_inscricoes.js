/* ==========================================================================
   GERENCIADOR DE MINHAS INSCRIÇÕES
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const inicializarTooltips = () => {
        if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip) return;
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
    };

    const configurarEventos = () => {
        // Confirmação e feedback visual ao cancelar inscrição em atividade
        document.querySelectorAll('.form-cancelar-atividade').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!confirm('Deseja realmente cancelar sua participação nesta atividade?')) {
                    e.preventDefault();
                    return;
                }

                const btn = form.querySelector('button[type="submit"]');
                if (btn) {
                    btn.disabled = true;
                    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Cancelando...';
                }
            });
        });

        // Impressão do Crachá no modal
        document.querySelectorAll('.btn-imprimir-cracha').forEach(btn => {
            btn.addEventListener('click', () => window.print());
        });
    };

    inicializarTooltips();
    configurarEventos();
});