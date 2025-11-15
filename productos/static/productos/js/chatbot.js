document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("chatbot-toggle");
    const chatBox = document.getElementById("chatbot-box");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");

    // Mostrar/ocultar chat
    toggleBtn.addEventListener("click", () => {
        chatBox.classList.toggle("visible");
    });

    // Enviar pregunta
    chatForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const pregunta = chatInput.value.trim();
        if (!pregunta) return;

        // Mostrar pregunta del usuario
        chatMessages.innerHTML += `<div class="mensaje usuario"><strong>Tú:</strong> ${pregunta}</div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;

        fetch("/chatbot/ask/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `pregunta=${encodeURIComponent(pregunta)}`
        })
        .then(res => res.json())
        .then(data => {
            // Convertir Markdown a HTML
            const htmlRespuesta = marked.parse(data.respuesta);

            chatMessages.innerHTML += `<div class="mensaje bot">
                <img class="botimg" src="/media/uploads/products/robot.png"> 
                <strong>Bot:</strong> ${htmlRespuesta}</div>`;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(err => {
            chatMessages.innerHTML += `<div class="mensaje bot">
                <strong>Bot:</strong> Ocurrió un error. Intenta de nuevo.</div>`;
        });

        chatInput.value = "";
    });
});
