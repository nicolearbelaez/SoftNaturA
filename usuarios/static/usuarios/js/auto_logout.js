(function() {
    const maxIdleTime = 1 * 60 * 1000;   // 1 minuto
    const warningTime = 30 * 1000;       // 30 segundos antes
    let idleTimer, warningTimer, countdownTimer;

    const modal = document.getElementById("logoutWarning");
    const countdownSpan = document.getElementById("countdown");

    function resetTimer() {
        clearTimeout(idleTimer);
        clearTimeout(warningTimer);
        clearInterval(countdownTimer);

        // Si existe modal, lo ocultamos (solo en páginas con baseP)
        if (modal) modal.style.display = "none";

        // Timer para mostrar el aviso
        warningTimer = setTimeout(() => {
            if (modal) showWarning();
        }, maxIdleTime - warningTime);

        // Timer para cerrar sesión
        idleTimer = setTimeout(autoLogout, maxIdleTime);
    }

    function showWarning() {
        let remaining = warningTime / 1000;

        modal.style.display = "block";
        countdownSpan.textContent = remaining;

        countdownTimer = setInterval(() => {
            remaining--;
            countdownSpan.textContent = remaining;

            if (remaining <= 0) {
                clearInterval(countdownTimer);
            }
        }, 1000);
    }

    function autoLogout() {
        window.location.href = "/usuarios/logout/?inactividad=1";
    }

    // Eventos que reinician el temporizador
    document.onmousemove = resetTimer;
    document.onkeypress = resetTimer;
    document.onclick = resetTimer;
    document.onscroll = resetTimer;
    window.onload = resetTimer;

    console.log("AutoLogout cargado correctamente.");
})();
