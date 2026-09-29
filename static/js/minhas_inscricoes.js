/* ==========================================================================
   MINHAS INSCRIÇÕES - JAVASCRIPT PRINCIPAL
   ========================================================================== */

   document.addEventListener('DOMContentLoaded', function () {

    /* ==========================================================================
       TOOLTIPS DO BOOTSTRAP
       ========================================================================== */

    const tooltipTriggerList = document.querySelectorAll(
        '[data-bs-toggle="tooltip"]'
    );

    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        if (
            typeof bootstrap !== 'undefined' &&
            bootstrap.Tooltip
        ) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        }
    });


    /* ==========================================================================
       ELEMENTOS PRINCIPAIS
       ========================================================================== */

    const paginaInscricoes = document.querySelector('.pagina-inscricoes');

    if (!paginaInscricoes) {
        return;
    }

    const inscricaoItens = document.querySelectorAll('.inscricao-item');
    const filtroBotoes = document.querySelectorAll('.filtro-btn');
    const campoBusca = document.querySelector('#campoBuscaInscricoes');

    const contadorEventos = document.querySelector('#contadorEventos');
    const contadorAtividades = document.querySelector('#contadorAtividades');
    const contadorProximas = document.querySelector('#contadorProximas');

    const mensagemBuscaVazia = document.querySelector('.empty-search-state');


    /* ==========================================================================
       CONTADORES DO RESUMO
       ========================================================================== */

    function atualizarContadores() {
        let totalEventos = inscricaoItens.length;
        let totalAtividades = 0;
        let totalProximas = 0;

        const agora = new Date();

        inscricaoItens.forEach(function (inscricao) {

            /* ------------------------------------------------------------------
               Conta as atividades da inscrição
               ------------------------------------------------------------------ */

            const atividades = inscricao.querySelectorAll(
                '.atividade-item'
            );

            totalAtividades += atividades.length;


            /* ------------------------------------------------------------------
               Conta atividades futuras
               ------------------------------------------------------------------ */

            atividades.forEach(function (atividade) {

                const dataAtividade = atividade.dataset.dataAtividade;

                if (!dataAtividade) {
                    return;
                }

                const data = new Date(dataAtividade);

                if (!isNaN(data.getTime()) && data >= agora) {
                    totalProximas++;
                }
            });
        });


        /* ----------------------------------------------------------------------
           Atualiza os valores na interface
           ---------------------------------------------------------------------- */

        if (contadorEventos) {
            contadorEventos.textContent = totalEventos;
        }

        if (contadorAtividades) {
            contadorAtividades.textContent = totalAtividades;
        }

        if (contadorProximas) {
            contadorProximas.textContent = totalProximas;
        }
    }


    /* ==========================================================================
       FILTROS DE INSCRIÇÕES
       ========================================================================== */

    function aplicarFiltro(filtroSelecionado) {

        const termoBusca = campoBusca
            ? campoBusca.value.trim().toLowerCase()
            : '';

        let quantidadeVisivel = 0;

        inscricaoItens.forEach(function (inscricao) {

            const status = (
                inscricao.dataset.status || ''
            ).toLowerCase();

            const textoInscricao = (
                inscricao.textContent || ''
            ).toLowerCase();

            let correspondeFiltro = true;
            let correspondeBusca = true;


            /* ------------------------------------------------------------------
               Filtro por categoria
               ------------------------------------------------------------------ */

            if (filtroSelecionado === 'proximas') {

                correspondeFiltro = verificarInscricaoFutura(inscricao);

            } else if (filtroSelecionado === 'concluidas') {

                correspondeFiltro = (
                    status === 'concluido' ||
                    status === 'concluída' ||
                    status === 'concluida'
                );

            } else if (filtroSelecionado === 'canceladas') {

                correspondeFiltro = (
                    status === 'cancelado' ||
                    status === 'cancelada'
                );
            }


            /* ------------------------------------------------------------------
               Filtro por busca
               ------------------------------------------------------------------ */

            if (termoBusca) {
                correspondeBusca = textoInscricao.includes(termoBusca);
            }


            /* ------------------------------------------------------------------
               Exibe ou oculta a inscrição
               ------------------------------------------------------------------ */

            if (correspondeFiltro && correspondeBusca) {

                inscricao.classList.remove('filtro-oculto');
                quantidadeVisivel++;

            } else {

                inscricao.classList.add('filtro-oculto');
            }
        });


        /* ----------------------------------------------------------------------
           Estado de busca sem resultados
           ---------------------------------------------------------------------- */

        if (mensagemBuscaVazia) {

            if (quantidadeVisivel === 0) {
                mensagemBuscaVazia.classList.remove('d-none');
            } else {
                mensagemBuscaVazia.classList.add('d-none');
            }
        }
    }


    /* ==========================================================================
       VERIFICAÇÃO DE ATIVIDADES FUTURAS
       ========================================================================== */

    function verificarInscricaoFutura(inscricao) {

        const atividades = inscricao.querySelectorAll(
            '.atividade-item'
        );

        const agora = new Date();

        for (const atividade of atividades) {

            const dataAtividade = atividade.dataset.dataAtividade;

            if (!dataAtividade) {
                continue;
            }

            const data = new Date(dataAtividade);

            if (!isNaN(data.getTime()) && data >= agora) {
                return true;
            }
        }

        return false;
    }


    /* ==========================================================================
       EVENTOS DOS BOTÕES DE FILTRO
       ========================================================================== */

    filtroBotoes.forEach(function (botao) {

        botao.addEventListener('click', function () {

            const filtroSelecionado = (
                botao.dataset.filtro || 'todos'
            );

            /* --------------------------------------------------------------
               Atualiza botão ativo
               -------------------------------------------------------------- */

            filtroBotoes.forEach(function (outroBotao) {
                outroBotao.classList.remove('active');
            });

            botao.classList.add('active');


            /* --------------------------------------------------------------
               Aplica o filtro
               -------------------------------------------------------------- */

            aplicarFiltro(filtroSelecionado);
        });
    });


    /* ==========================================================================
       CAMPO DE BUSCA
       ========================================================================== */

    if (campoBusca) {

        campoBusca.addEventListener('input', function () {

            const botaoAtivo = document.querySelector(
                '.filtro-btn.active'
            );

            const filtroAtual = botaoAtivo
                ? botaoAtivo.dataset.filtro
                : 'todos';

            aplicarFiltro(filtroAtual);
        });
    }


    /* ==========================================================================
       CANCELAMENTO DE ATIVIDADE
       ========================================================================== */

    const botoesCancelar = document.querySelectorAll(
        '.btn-cancelar-atividade'
    );

    botoesCancelar.forEach(function (botao) {

        botao.addEventListener('click', function (event) {

            const confirmacao = confirm(
                'Deseja realmente cancelar sua participação nesta atividade?'
            );


            /* ------------------------------------------------------------------
               Usuário cancelou a confirmação
               ------------------------------------------------------------------ */

            if (!confirmacao) {
                event.preventDefault();
                return;
            }


            /* ------------------------------------------------------------------
               Estado de carregamento
               ------------------------------------------------------------------ */

            botao.classList.add('disabled');

            botao.setAttribute(
                'aria-disabled',
                'true'
            );

            botao.innerHTML = `
                <span
                    class="spinner-border spinner-border-sm me-1"
                    role="status"
                    aria-hidden="true">
                </span>
                Cancelando...
            `;
        });
    });


    /* ==========================================================================
       IMPRESSÃO DO CRACHÁ
       ========================================================================== */

    const botoesImprimir = document.querySelectorAll(
        '.btn-imprimir-cracha'
    );

    botoesImprimir.forEach(function (botao) {

        botao.addEventListener('click', function () {
            window.print();
        });
    });


    /* ==========================================================================
       INICIALIZAÇÃO
       ========================================================================== */

    atualizarContadores();

    aplicarFiltro('todos');

});