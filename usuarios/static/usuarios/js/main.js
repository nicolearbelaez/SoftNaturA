if (document.body.dataset.page === "baseU") {
  document.addEventListener('DOMContentLoaded', () => {
    // Efecto en las tarjetas
    const cards = document.querySelectorAll('.card[data-url]');
    cards.forEach(card => {
      card.addEventListener('click', () => {
        window.location.href = card.getAttribute('data-url');
      });
    });

  });

}

// Hacer las cards clicables
if (document.body.dataset.page === "dashboard") {
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.card[data-url]').forEach(card => {
      card.addEventListener('click', function () {
        window.location.href = this.dataset.url;
      });
    });
  });

}


if (document.body.dataset.page === "register") {
  function validarRegistro() {
    let nombre = document.getElementById("id_nombre").value.trim();
    let pass1 = document.getElementById("id_password1").value.trim();
    let pass2 = document.getElementById("id_password2").value.trim();
    let email = document.getElementById("id_email").value.trim();
    let telefono = document.getElementById("id_phone_number").value.trim();

    let msgNombre = document.getElementById("msg-nombre");
    let msgPass = document.getElementById("msg-pass");
    let msgConfirm = document.getElementById("msg-confirm");
    let msgEmail = document.getElementById("msg-email");
    let msgTelefono = document.getElementById("msg-telefono");

    let valido = true;

    // Limpiar mensajes
    msgNombre.textContent = "";
    msgPass.textContent = "";
    msgConfirm.textContent = "";
    msgEmail.textContent = "";
    msgTelefono.textContent = "";
    msgConfirm.className = "mensaje-error";

    // Validar nombre
    if (nombre === "") {
      msgNombre.textContent = "**El nombre es obligatorio.**";
      valido = false;
    }

    // Validar email
    if (email === "") {
      msgEmail.textContent = "**El email es obligatorio.**";
      valido = false;
    }

    // Validar teléfono
    if (telefono === "") {
      msgTelefono.textContent = "**El teléfono es obligatorio.**";
      valido = false;
    }

    // Validar contraseña
    let regex = /^(?=.*[A-Z])(?=.*[\W_]).{8,}$/;
    if (pass1 === "") {
      msgPass.textContent = "**La contraseña es obligatoria.**";
      valido = false;
    } else if (!regex.test(pass1)) {
      msgPass.textContent = "**Debe tener mínimo 8 caracteres, una mayúscula y un símbolo.**";
      valido = false;
    }

    // Confirmar contraseña
    if (pass2 === "") {
      msgConfirm.textContent = "**Repite la contraseña.**";
      valido = false;
    } else if (pass1 !== pass2) {
      msgConfirm.textContent = "**Las contraseñas no coinciden.**";
      valido = false;
    } else if (regex.test(pass1)) {
      msgConfirm.textContent = "**Contraseñas coinciden.**";
      msgConfirm.className = "mensaje-ok";
    }

    return valido;
  }

}


if (document.body.dataset.page === "editar-perfil") {
    // Simulación de manejo del formulario (en producción esto lo manejaría Django)
    document.getElementById('profileForm').addEventListener('submit', function (e) {
      e.preventDefault();

      const formData = new FormData(this);
      const nombre = formData.get('first_name');
      const email = formData.get('email');

      if (nombre && email) {
        alert('Perfil actualizado correctamente\n\nNombre: ' + nombre + '\nEmail: ' + email);
      }
    });
}

document.querySelectorAll(".dropdown-btn").forEach(btn => {
    btn.addEventListener("click", function() {
        this.classList.toggle("active");
        const container = this.nextElementSibling;
        if (container.style.display === "flex") {
            container.style.display = "none";
        } else {
            container.style.display = "flex";
        }
    });
});
