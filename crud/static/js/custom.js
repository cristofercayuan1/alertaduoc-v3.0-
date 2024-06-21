// Función para ocultar el mensaje después de 2 segundos
setTimeout(function() {
    document.querySelectorAll('.message').forEach(function(element) {
        element.style.display = 'none';
    });
}, 3000); // 3000 milisegundos = 2 segundos


