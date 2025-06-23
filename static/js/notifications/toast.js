function showToast(message, type = "primary") {
    const toastEl = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toastMessage');

    // Cambiar clase del toast según tipo
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;

    toastMessage.textContent = message;

    // Mostrar el toast
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}
