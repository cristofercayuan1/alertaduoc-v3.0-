// JavaScript para manejar el registro asíncrono
document.addEventListener('DOMContentLoaded', function () {
    const registrationForm = document.getElementById('registration-form');
    registrationForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(registrationForm);
        fetch('/register/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // Para identificar la solicitud AJAX
                'X-CSRFToken': '{{ csrf_token }}' // Token CSRF
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al registrar el usuario');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('registration-success').style.display = 'block';
            registrationForm.reset(); // Reiniciar el formulario después del registro exitoso
        })
        .catch(error => {
            console.error('Error:', error);
            // Manejar errores de validación del formulario si es necesario
        });
    });
    
    form.addEventListener("submit", function(event) {
        var inputs = form.querySelectorAll("input");
        inputs.forEach(function(input) {
            if (input.value.trim() === "") {
                input.classList.add("is-invalid");
                event.preventDefault(); // Evita que se envíe el formulario si hay campos vacíos
            } else {
                input.classList.remove("is-invalid");
            }
        });
    });
});
