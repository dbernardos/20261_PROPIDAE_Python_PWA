/* ==========================================================================
   GERENCIADOR DE MINHAS INSCRIÇÕES
   ========================================================================== */

   document.addEventListener('DOMContentLoaded', () => {
    // 1. Elementos da Interface
    const paginaInscricoes = document.querySelector('.pagina-inscricoes');
    if (!paginaInscricoes) return;

    const cardsInscricao = document.querySelectorAll('.inscricao-item');

    // Elementos dos Contadores do Topo
    const elContadorEventos = document.querySelector('[data-contador-eventos]') || document.querySelector('#contadorEventos');
    const elContadorAtividades = document.querySelector('[data-contador-atividades]') || document.querySelector('#contadorAtividades');

    /* ==========================================================================
       INICIALIZAÇÃO DE COMPONENTES
       ========================================================================== */
    const inicializarTooltips = () => {
        const triggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        triggers.forEach(el => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                new bootstrap.Tooltip(el);
            }
        });
    };

    /* ==========================================================================
       CÁLCULO E ATUALIZAÇÃO DOS CONTADORES
       ========================================================================== */
    const atualizarContadores = () => {
        const totalEventos = cardsInscricao.length;
        let totalAtividades = 0;

        cardsInscricao.forEach(card => {
            const linhasAtividades = card.querySelectorAll('.atividade-linha');
            const qtdAtividadesCard = linhasAtividades.length;
            totalAtividades += qtdAtividadesCard;

            // Atualiza os indicadores do card do evento
            const badgeCard = card.querySelector('[data-contador-evento-badge]');
            const spanCard = card.querySelector('[data-contador-evento]');
            if (badgeCard) badgeCard.textContent = qtdAtividadesCard;
            if (spanCard) spanCard.textContent = qtdAtividadesCard;
        });

        // Atualiza os números no topo da página
        if (elContadorEventos) elContadorEventos.textContent = totalEventos;
        if (elContadorAtividades) elContadorAtividades.textContent = totalAtividades;
    };

    /* ==========================================================================
       CONFIGURAÇÃO DE EVENTOS DO UTILIZADOR
       ========================================================================== */
    const configurarEventos = () => {
        // Evento nos botões de cancelar atividade
        document.querySelectorAll('.btn-cancelar-atividade').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const confirmacao = confirm('Deseja realmente cancelar sua participação nesta atividade?');
                if (!confirmacao) {
                    e.preventDefault();
                    return;
                }
                btn.classList.add('disabled');
                btn.setAttribute('aria-disabled', 'true');
                btn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                    Cancelando...
                `;
            });
        });

        // Evento de Impressão do Crachá
        document.querySelectorAll('.btn-imprimir-cracha').forEach(btn => {
            btn.addEventListener('click', () => window.print());
        });
    };

    /* ==========================================================================
       EXECUÇÃO INICIAL
       ========================================================================== */
    inicializarTooltips();
    atualizarContadores();
    configurarEventos();
});