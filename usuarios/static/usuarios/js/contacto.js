// Variable para verificar si el usuario está logueado
const usuarioLogueado = document.querySelector('[data-user-authenticated]').dataset.userAuthenticated === 'true';

// Variables globales
let emailValido = false;
let verificandoEmail = false;
let timeoutVerificacion = null;

// Obtener elementos del DOM
const correoInput = document.getElementById('correo');
const emailStatus = document.getElementById('emailStatus');
const contactForm = document.getElementById('contactForm');
const btnEnviar = document.getElementById('btnEnviar');

// Función para validar el formato del correo electrónico
function validarFormatoEmail(email) {
  const regex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return regex.test(email);
}

// Función para verificar si el correo existe realmente usando API gratuita
async function verificarEmailExiste(email) {
  try {
    const API_KEY = 'test';
    const response = await fetch(
      `https://emailvalidation.abstractapi.com/v1/?api_key=${API_KEY}&email=${encodeURIComponent(email)}`
    );

    if (!response.ok) {
      throw new Error('Error en la API');
    }

    const data = await response.json();
    console.log('Respuesta API:', data);

    if (data.is_disposable_email && data.is_disposable_email.value === true) {
      return { valido: false, mensaje: 'No se permiten correos temporales o desechables' };
    }

    if (data.quality_score) {
      const score = parseFloat(data.quality_score);
      if (score < 0.5) {
        return { valido: false, mensaje: 'El correo parece no ser válido' };
      }
    }

    if (data.is_valid_format && data.is_valid_format.value === false) {
      return { valido: false, mensaje: 'Formato de correo inválido' };
    }

    if (data.is_mx_found && data.is_mx_found.value === false) {
      return { valido: false, mensaje: 'El dominio no puede recibir correos' };
    }

    if (data.is_smtp_valid && data.is_smtp_valid.value === false) {
      return { valido: false, mensaje: 'El servidor de correo no está disponible' };
    }

    if (data.deliverability) {
      if (data.deliverability === 'UNDELIVERABLE') {
        return { valido: false, mensaje: 'Este correo no puede recibir mensajes' };
      }
      if (data.deliverability === 'RISKY') {
        return { valido: false, mensaje: 'El correo es de riesgo. Usa uno diferente' };
      }
    }

    return { valido: true, mensaje: 'Correo verificado' };

  } catch (error) {
    console.error('Error al verificar email:', error);

    const regex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const dominiosPopulares = [
      'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'yahoo.es',
      'live.com', 'icloud.com', 'hotmail.es', 'outlook.es'
    ];

    if (!regex.test(email)) {
      return { valido: false, mensaje: 'Formato de correo inválido' };
    }

    const partes = email.split('@');
    const usuario = partes[0];
    const dominio = partes[1]?.toLowerCase();

    if (usuario.length < 3) {
      return { valido: false, mensaje: 'El correo es demasiado corto' };
    }

    if (!dominiosPopulares.includes(dominio)) {
      return { valido: false, mensaje: 'Por favor usa Gmail, Hotmail, Outlook o Yahoo' };
    }

    return { valido: true, mensaje: 'Correo valido' };
  }
}

// Función para mostrar el estado de verificación
function mostrarEstado(tipo, mensaje) {
  emailStatus.className = `email-status ${tipo}`;

  if (tipo === 'checking') {
    emailStatus.innerHTML = '<div class="spinner"></div><span>Verificando correo...</span>';
    correoInput.classList.remove('valid', 'invalid');
    correoInput.classList.add('checking');
    btnEnviar.disabled = true;
  } else if (tipo === 'valid') {
    emailStatus.innerHTML = `<i class="fas fa-check-circle"></i><span>${mensaje}</span>`;
    correoInput.classList.remove('invalid', 'checking');
    correoInput.classList.add('valid');
    btnEnviar.disabled = false;
    emailValido = true;
  } else if (tipo === 'invalid') {
    emailStatus.innerHTML = `<i class="fas fa-times-circle"></i><span>${mensaje}</span>`;
    correoInput.classList.remove('valid', 'checking');
    correoInput.classList.add('invalid');
    btnEnviar.disabled = true;
    emailValido = false;
  } else {
    emailStatus.innerHTML = '';
    correoInput.classList.remove('valid', 'invalid', 'checking');
    btnEnviar.disabled = false;
  }
}

// Evento cuando el usuario escribe en el campo de correo
correoInput.addEventListener('input', function () {
  const email = this.value.trim();

  if (usuarioLogueado) {
    mostrarEstado('', '');
    return;
  }

  if (timeoutVerificacion) {
    clearTimeout(timeoutVerificacion);
  }

  if (!email) {
    mostrarEstado('', '');
    emailValido = false;
    return;
  }

  if (!validarFormatoEmail(email)) {
    mostrarEstado('invalid', 'Formato de correo inválido');
    emailValido = false;
    return;
  }

  timeoutVerificacion = setTimeout(async () => {
    mostrarEstado('checking', 'Verificando...');
    verificandoEmail = true;

    const resultado = await verificarEmailExiste(email);

    if (resultado.valido) {
      mostrarEstado('valid', resultado.mensaje);
    } else {
      mostrarEstado('invalid', resultado.mensaje);
    }

    verificandoEmail = false;
  }, 1000);
});

// Validación al enviar el formulario
contactForm.addEventListener('submit', function (e) {
  e.preventDefault();

  console.log("📝 Formulario enviado");
  console.log("📱 Número admin:", numeroAdministracion);

  const correo = correoInput.value.trim();

  // Si el usuario NO está logueado, validar el correo
  if (!usuarioLogueado) {
    if (!validarFormatoEmail(correo)) {
      mostrarEstado('invalid', 'Por favor ingresa un correo válido');
      correoInput.focus();
      return false;
    }

    if (verificandoEmail) {
      mostrarEstado('checking', 'Espera mientras verificamos el correo...');
      return false;
    }

    if (!emailValido) {
      mostrarEstado('invalid', 'Por favor usa un correo electrónico válido');
      correoInput.focus();
      return false;
    }
  }

  // Obtener los valores del formulario
  const nombre = document.getElementById('nombre').value;
  const asunto = document.getElementById('asunto').value;
  const mensaje = document.getElementById('mensaje').value;

  // Crear el mensaje para WhatsApp
  const mensajeWhatsApp = `*NUEVO MENSAJE DE CONTACTO*%0A%0A` +
    `*Nombre:* ${encodeURIComponent(nombre)}%0A` +
    `*Correo:* ${encodeURIComponent(correo)}%0A` +
    `*Asunto:* ${encodeURIComponent(asunto)}%0A%0A` +
    `*Mensaje:*%0A${encodeURIComponent(mensaje)}`;

  // ✅ USAR BACKTICKS PARA INTERPOLACIÓN
  const numeroWhatsApp = `57${numeroAdministracion}`;
  const urlWhatsApp = `https://wa.me/${numeroWhatsApp}?text=${mensajeWhatsApp}`;
  
  console.log("🔗 URL generada:", urlWhatsApp);

  // Abrir WhatsApp
  window.open(urlWhatsApp, '_blank');

  // Limpiar el formulario y estados
  contactForm.reset();
  mostrarEstado('', '');
  emailValido = false;
});