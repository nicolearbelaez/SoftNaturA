    function mostrarAlerta(titulo, mensaje, redirigir = false, url = '/usuarios/loginAdm/') {
      document.getElementById('alert-title').innerText = titulo;
      document.getElementById('alert-message').innerText = mensaje;
      const alertBox = document.getElementById('custom-alert');
      alertBox.style.display = 'flex';
      alertBox.dataset.redirigir = redirigir;
      alertBox.dataset.url = url;
    }

    function cerrarAlerta() {
      const alertBox = document.getElementById('custom-alert');
      const redirigir = alertBox.dataset.redirigir === 'true';
      const url = alertBox.dataset.url;

      document.getElementById('custom-alert').style.display = 'none';

      if (redirigir) {
        window.location.href = url;
      }
    }

    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');
    let intentosCodigo = 0;

    document.getElementById('btnStep1').addEventListener('click', async function () {
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const btnStep1 = this;

      if (!email || !password) {
        mostrarAlerta('Campos incompletos', 'Por favor, completa todos los campos.');
        return;
      }

      btnStep1.disabled = true;
      btnStep1.textContent = 'Enviando código...';

      try {
        const response = await fetch('/usuarios/enviar-codigo-verificacion/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          },
          body: JSON.stringify({ email: email, password: password }),
          credentials: 'same-origin' // muy importante
        });

        const data = await response.json();

        if (data.success) {
          document.getElementById('emailVerified').value = email;
          document.getElementById('passwordVerified').value = password;

          document.getElementById('step1').classList.remove('active');
          document.getElementById('step2').classList.add('active');
          document.getElementById('dot1').classList.remove('active');
          document.getElementById('dot2').classList.add('active');
          document.getElementById('subtitulo').textContent = 'Verificación de seguridad';
          document.getElementById('digit1').focus();
          iniciarTemporizador();
          intentosCodigo = 0; // reiniciamos contador
        } else {
          mostrarAlerta('Error', data.mensaje || 'Error al enviar el código. Verifica tus credenciales.');
        }
      } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('Error de conexión', 'Por favor, intenta nuevamente.');
      } finally {
        btnStep1.disabled = false;
        btnStep1.textContent = 'Continuar';
      }
    });

    // Manejo de inputs del código
    const codeDigits = document.querySelectorAll('.code-digit');

    codeDigits.forEach((digit, index) => {
      digit.addEventListener('input', function (e) {
        if (e.target.value.length === 1 && index < codeDigits.length - 1) {
          codeDigits[index + 1].focus();
        }
        actualizarCodigoCompleto();
      });

      digit.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !e.target.value && index > 0) {
          codeDigits[index - 1].focus();
        }
      });

      digit.addEventListener('keypress', function (e) {
        if (!/[0-9]/.test(e.key)) e.preventDefault();
      });

      digit.addEventListener('paste', function (e) {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').slice(0, 6);
        pastedData.split('').forEach((char, i) => {
          if (codeDigits[i] && /[0-9]/.test(char)) codeDigits[i].value = char;
        });
        actualizarCodigoCompleto();
      });
    });

    function actualizarCodigoCompleto() {
      const codigo = Array.from(codeDigits).map(d => d.value).join('');
      document.getElementById('codigoCompleto').value = codigo;
    }

    document.getElementById('btnVolver').addEventListener('click', function () {
      document.getElementById('step2').classList.remove('active');
      document.getElementById('step1').classList.add('active');
      document.getElementById('dot2').classList.remove('active');
      document.getElementById('dot1').classList.add('active');
      document.getElementById('subtitulo').textContent = 'Acceso al sistema de administración';
      codeDigits.forEach(d => d.value = '');
    });

    let tiempoRestante = 60;
    let intervalo;

    function iniciarTemporizador() {
      tiempoRestante = 60;
      document.getElementById('btnReenviar').disabled = true;

      intervalo = setInterval(() => {
        tiempoRestante--;
        document.getElementById('temporizador').textContent =
          `Puedes reenviar el código en ${tiempoRestante}s`;

        if (tiempoRestante <= 0) {
          clearInterval(intervalo);
          document.getElementById('btnReenviar').disabled = false;
          document.getElementById('temporizador').textContent = '';
        }
      }, 1000);
    }

    document.getElementById('btnReenviar').addEventListener('click', async function () {
      const email = document.getElementById('emailVerified').value;
      const password = document.getElementById('passwordVerified').value;
      const btnReenviar = this;

      btnReenviar.disabled = true;
      btnReenviar.textContent = 'Reenviando...';

      try {
        const response = await fetch('/usuarios/enviar-codigo-verificacion/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          },
          body: JSON.stringify({ email: email, password: password }),
          credentials: 'same-origin'
        });

        const data = await response.json();

        if (data.success) {
          codeDigits.forEach(d => d.value = '');
          document.getElementById('digit1').focus();
          iniciarTemporizador();
          mostrarAlerta('Código reenviado', 'Se ha enviado un nuevo código a tu correo.');
          intentosCodigo = 0; // reiniciamos contador al reenviar
        } else {
          mostrarAlerta('Error', data.mensaje || 'Error al reenviar el código.');
          btnReenviar.disabled = false;
        }
      } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('Error de conexión', 'Por favor, intenta nuevamente.');
        btnReenviar.disabled = false;
      } finally {
        btnReenviar.textContent = 'Reenviar código';
      }
    });

    // Validación y envío del código
    document.getElementById('loginForm').addEventListener('submit', async function (e) {
      e.preventDefault();

      const codigo = document.getElementById('codigoCompleto').value;
      const email = document.getElementById('emailVerified').value;
      const password = document.getElementById('passwordVerified').value;
      const btnVerificar = document.getElementById('btnVerificar');

      if (codigo.length !== 6) {
        mostrarAlerta('Código incompleto', 'Por favor, ingresa los 6 dígitos del código de verificación.');
        return;
      }

      btnVerificar.disabled = true;
      btnVerificar.textContent = 'Verificando...';

      try {
        const response = await fetch('/usuarios/verificar-codigo/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          },
          body: JSON.stringify({
            email: email,
            password: password,
            codigo_verificacion: codigo
          }),
          credentials: 'same-origin'  // ✅ MUY IMPORTANTE
        });


        const data = await response.json();

        if (data.success) {
          mostrarAlerta('Acceso concedido', data.mensaje, true, data.redirect_url);
        } else {
          if (data.redirect) {
            mostrarAlerta('Error', data.mensaje, true, '/usuarios/loginAdm/');
          } else {
            intentosCodigo++;
            mostrarAlerta('Error de verificación', data.mensaje);
            btnVerificar.disabled = false;
          }
        }

      } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('Error de conexión', 'No se pudo verificar el código. Intenta nuevamente.');
        btnVerificar.disabled = false;
      } finally {
        btnVerificar.textContent = 'Verificar y Entrar';
      }
    });