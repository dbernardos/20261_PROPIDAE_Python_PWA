/* ==========================================================================
   GERENCIADOR DE MINHAS INSCRIÇÕES
   ========================================================================== */

   document.addEventListener('DOMContentLoaded', () => {
    // 1. Elementos da Interface
    const paginaInscricoes = document.querySelector('.pagina-inscricoes');
    if (!paginaInscricoes) return;

    const cardsInscricao = document.querySelectorAll('.inscricao-item');
    const campoBusca = document.querySelector('#buscaInscricoes') || document.querySelector('#campoBuscaInscricoes');
    const botoesFiltro = document.querySelectorAll('.filtro-btn');
    const mensagemSemResultados = document.querySelector('#semResultadosBusca');

    // Elementos dos Contadores
    const elContadorEventos = document.querySelector('#contadorEventos');
    const elContadorAtividades = document.querySelector('#contadorAtividades');
    const elContadorProximas = document.querySelector('#contadorProximas');

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
       MÉTODOS AUXILIARES DE DATA
       ========================================================================== */
    const extrairDataAtividade = (linhaAtividade) => {
        // Tenta pelo atributo ISO data-inicio
        const dataISO = linhaAtividade.dataset.inicio || linhaAtividade.dataset.dataAtividade;
        if (dataISO) {
            const dataObj = new Date(dataISO);
            if (!isNaN(dataObj.getTime())) return dataObj;
        }

        // Fallback: Tenta converter o texto renderizado no HTML ex: "29/09/2026 19:10"
        const txtHorario = linhaAtividade.querySelector('.atividade-horario span')?.textContent.trim();
        if (txtHorario) {
            const [dataPart, horaPart] = txtHorario.split(' ');
            if (dataPart && horaPart) {
                const [dia, mes, ano] = dataPart.split('/');
                const [hora, min] = horaPart.split(':');
                return new Date(ano, mes - 1, dia, hora, min);
            }
        }
        return null;
    };

    /* ==========================================================================
       CÁLCULO E ATUALIZAÇÃO DOS CONTADORES
       ========================================================================== */
    const atualizarContadores = () => {
        const totalEventos = cardsInscricao.length;
        let totalAtividades = 0;
        let totalProximas = 0;
        const agora = new Date();

        cardsInscricao.forEach(card => {
            const linhasAtividades = card.querySelectorAll('.atividade-linha');
            const qtdAtividadesCard = linhasAtividades.length;
            totalAtividades += qtdAtividadesCard;

            // Atualiza os indicadores dentro do card do evento
            const badgeCard = card.querySelector('[data-contador-evento-badge]');
            const spanCard = card.querySelector('[data-contador-evento]');
            if (badgeCard) badgeCard.textContent = qtdAtividadesCard;
            if (spanCard) spanCard.textContent = qtdAtividadesCard;

            // Verifica atividades no futuro
            linhasAtividades.forEach(linha => {
                const dataAtividade = extrairDataAtividade(linha);
                if (dataAtividade && dataAtividade >= agora) {
                    totalProximas++;
                }
            });
        });

        // Atualiza os números no topo da página
        if (elContadorEventos) elContadorEventos.textContent = totalEventos;
        if (elContadorAtividades) elContadorAtividades.textContent = totalAtividades;
        if (elContadorProximas) elContadorProximas.textContent = totalProximas;
    };

    /* ==========================================================================
       LÓGICA DE FILTRAGEM E BUSCA
       ========================================================================== */
    const possuiAtividadeFutura = (card) => {
        const agora = new Date();
        const linhasAtividades = card.querySelectorAll('.atividade-linha');

        for (const linha of linhasAtividades) {
            const dataAtividade = extrairDataAtividade(linha);
            if (dataAtividade && dataAtividade >= agora) {
                return true;
            }
        }
        return false;
    };

    const aplicarFiltrosEBusca = () => {
        const termoBusca = campoBusca ? campoBusca.value.trim().toLowerCase() : '';
        const botaoAtivo = document.querySelector('.filtro-btn.active');
        const filtroAtual = botaoAtivo ? botaoAtivo.dataset.filtro : 'todos';

        let cartoesVisiveis = 0;

        cardsInscricao.forEach(card => {
            const statusCard = (card.dataset.status || '').toLowerCase();
            const textoCard = card.textContent.toLowerCase();

            // 1. Checa texto digitado na busca
            const correspondeBusca = !termoBusca || textoCard.includes(termoBusca);

            // 2. Checa o botão de filtro ativo
            let correspondeFiltro = true;
            if (filtroAtual === 'proximas') {
                correspondeFiltro = possuiAtividadeFutura(card);
            } else if (filtroAtual === 'concluidas') {
                correspondeFiltro = statusCard.includes('concluid');
            } else if (filtroAtual === 'canceladas') {
                correspondeFiltro = statusCard.includes('cancelad');
            }

            // Exibe ou esconde
            if (correspondeBusca && correspondeFiltro) {
                card.classList.remove('d-none');
                cartoesVisiveis++;
            } else {
                card.classList.add('d-none');
            }
        });

        // Exibe mensagem de "Nenhum resultado encontrado" se necessário
        if (mensagemSemResultados) {
            if (cartoesVisiveis === 0 && cardsInscricao.length > 0) {
                mensagemSemResultados.classList.remove('d-none');
            } else {
                mensagemSemResultados.classList.add('d-none');
            }
        }
    };

    /* ==========================================================================
       CONFIGURAÇÃO DE EVENTOS DO USUÁRIO
       ========================================================================== */
    const configurarEventos = () => {
        // Evento nos botões de filtro
        botoesFiltro.forEach(btn => {
            btn.addEventListener('click', () => {
                botoesFiltro.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                aplicarFiltrosEBusca();
            });
        });

        // Evento no input de busca em tempo real
        if (campoBusca) {
            campoBusca.addEventListener('input', aplicarFiltrosEBusca);
        }

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
    aplicarFiltrosEBusca();
});