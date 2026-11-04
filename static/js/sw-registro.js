if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker
            .register('/service-worker.js')
            .then((registration) => {
                console.log('Service-worker registrado com sucesso:', registration.scope)
            })
            .catch((error) => {
                console.log('Falha ao registrar Service Worker:', error)
            })
    })
} else {
    console.log('Service Worker não é suportado neste navegador.')
}