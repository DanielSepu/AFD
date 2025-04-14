$(document).ready(function() {
    $('.toggle-button').on('click', function() {
        // Busca el contenido a desplegar en el mismo fieldset
        $(this).closest('fieldset').find('.toggle-content').toggle();

        // Cambia el ícono de la flecha
        $(this).find('i').toggleClass('fa-chevron-down fa-chevron-up');
    });
});