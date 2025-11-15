const page = document.querySelector("[data-page='devoluciones']");

if (page) {
    console.log("JS cargado para gestión de devoluciones");
    var devolucionesData = [];

    try {
        devolucionesData = JSON.parse(document.getElementById('datosJson').textContent || '[]');
    } catch (e) {
        console.error("Error al parsear devoluciones_json:", e);
    }

    function verDetalles(id) {
        id = parseInt(id); // ✅ asegura que sea número
        var devolucion = devolucionesData.find(function (d) { return d.id === id; });
        if (!devolucion) return;

        var fotosHTML = '';
        if (devolucion.fotos && devolucion.fotos.length > 0) {
            fotosHTML = '<div class="galeria-fotos">';
            for (var i = 0; i < devolucion.fotos.length; i++) {
                var foto = devolucion.fotos[i];
                fotosHTML += '<div class="foto-item-modal" onclick="verImagenGrande(\'' + foto + '\')">';
                fotosHTML += '<img src="' + foto + '" alt="Foto del producto">';
                fotosHTML += '</div>';
            }
            fotosHTML += '</div>';
        } else {
            fotosHTML = '<div class="sin-fotos"><i class="fa fa-image"></i><p>No se adjuntaron fotos</p></div>';
        }

        var accionesHTML = '';
        if (devolucion.estado === 'Pendiente') {
            accionesHTML = '<div class="acciones-modal">';
            accionesHTML += '<form method="POST" action="/usuarios/aprobar-devolucion/' + devolucion.id + '/" style="display: inline;">';
            accionesHTML += '<input type="hidden" name="csrfmiddlewaretoken" value="' + getCookie('csrftoken') + '">';
            accionesHTML += '<button type="submit" class="btn-aprobar" style="padding: 12px 24px; font-size: 1rem;">';
            accionesHTML += '<i class="fa fa-check"></i> Aprobar Devolución</button></form>';
            accionesHTML += '<form method="POST" action="/usuarios/rechazar-devolucion/' + devolucion.id + '/" style="display: inline;">';
            accionesHTML += '<input type="hidden" name="csrfmiddlewaretoken" value="' + getCookie('csrftoken') + '">';
            accionesHTML += '<button type="submit" class="btn-rechazar" style="padding: 12px 24px; font-size: 1rem;">';
            accionesHTML += '<i class="fa fa-times"></i> Rechazar Devolución</button></form>';
            accionesHTML += '</div>';
        }

        var contenido = `
            <div class="detalle-seccion">
                <h4><i class="fa fa-user"></i> Información del Cliente</h4>
                <div class="detalle-info">
                    <p><strong>Nombre:</strong> ${devolucion.usuario_nombre}</p>
                    <p><strong>Email:</strong> ${devolucion.usuario_email}</p>
                </div>
            </div>

            <div class="detalle-seccion">
                <h4><i class="fa fa-box"></i> Información del Producto</h4>
                <div class="detalle-info">
                    <p><strong>Producto:</strong> ${devolucion.producto_nombre}</p>
                    <p><strong>Pedido:</strong> #${devolucion.pedido_id}</p>
                    <p><strong>Fecha de solicitud:</strong> ${devolucion.fecha}</p>
                </div>
            </div>

            <div class="detalle-seccion">
                <h4><i class="fa fa-comment-dots"></i> Motivo de la Devolución</h4>
                <div class="detalle-info">
                    <p>${devolucion.motivo}</p>
                </div>
            </div>

            <div class="detalle-seccion">
                <h4><i class="fa fa-camera"></i> Fotos del Producto</h4>
                ${fotosHTML}
            </div>

            ${accionesHTML}
        `;

        document.getElementById('contenidoModal').innerHTML = contenido;
        document.getElementById('modalDetalles').classList.add('active');
    }

    function cerrarModal() {
        document.getElementById('modalDetalles').classList.remove('active');
    }

    function verImagenGrande(src) {
        document.getElementById('imagenGrande').src = src;
        document.getElementById('modalImagen').classList.add('active');
    }

    function cerrarImagen() {
        document.getElementById('modalImagen').classList.remove('active');
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}


const page1 = document.querySelector("[data-page='gst-usuarios']");

if (page1) {
    console.log("JS cargado para gestión de usuarios");
    let filaSeleccionada = null;

    // ================= MODALES =================
    function abrirModalAgregar() {
        document.getElementById("modal-agregar").style.display = "block";
        document.getElementById("modal-overlay").style.display = "block";
        document.body.style.overflow = "hidden";
    }

    function cerrarModalAgregar() {
        document.getElementById("modal-agregar").style.display = "none";
        document.getElementById("modal-overlay").style.display = "none";
        document.body.style.overflow = "";
    }

    function abrirModalEditar() {
        document.getElementById("modal-editar").style.display = "block";
        document.getElementById("modal-overlay").style.display = "block";
        document.body.style.overflow = "hidden";
    }

    function cerrarModalEditar() {
        document.getElementById("modal-editar").style.display = "none";
        document.getElementById("modal-overlay").style.display = "none";
        document.body.style.overflow = "";
    }

    function cerrarTodosLosModales() {
        cerrarModalAgregar();
        cerrarModalEditar();
    }


    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".editar:not([disabled])").forEach((boton) => {
            boton.addEventListener("click", function (e) {
                e.preventDefault();

                let userId = boton.dataset.id;

                // Rellenar modal
                document.getElementById("editar-id").value = userId;
                document.getElementById("editar-nombre").value = boton.dataset.nombre || "";
                document.getElementById("editar-email").value = boton.dataset.email || "";
                document.getElementById("editar-telefono").value = boton.dataset.telefono || "";
                document.getElementById("editar-rol").value = boton.dataset.rol || "cliente";

                // Pone la URL correcta
                document.getElementById("form-editar").action = `/usuarios/editar/${userId}/`;

                abrirModalEditar();
            });
        });
    });

    // ================= BUSCADOR UNIVERSAL =================
    function configurarBuscador(inputId, tableId, statsId, textoEntidad) {
        const searchInput = document.getElementById(inputId);
        const searchStats = statsId ? document.getElementById(statsId) : null;
        const tbody = document.querySelector(`#${tableId} tbody`);
        const rows = tbody ? tbody.querySelectorAll('tr[data-search-text]') : document.querySelectorAll(`#${tableId} tr[data-search-text]`);
        const totalRows = rows.length;

        function actualizarEstadisticas() {
            if (!searchStats) return;
            const visibles = Array.from(rows).filter(r => r.style.display !== 'none').length;

            if (searchInput.value.trim() === "") {
                searchStats.textContent = `Mostrando ${totalRows} ${textoEntidad}${totalRows !== 1 ? 's' : ''}`;
            } else {
                searchStats.textContent = `Encontrados ${visibles} de ${totalRows} ${textoEntidad}${totalRows !== 1 ? 's' : ''}`;
            }
        }

        if (searchInput) {
            actualizarEstadisticas();
            searchInput.addEventListener("input", function () {
                const searchTerm = this.value.toLowerCase().trim();

                rows.forEach(row => {
                    const searchText = row.dataset.searchText || "";
                    row.style.display = (searchTerm === "" || searchText.includes(searchTerm)) ? "" : "none";
                });

                actualizarEstadisticas();
            });
        }
    }

    // 🔹 Configurar buscadores
    configurarBuscador("searchInput", "usuariosTable", "searchStatsUsuarios", "usuario");
    configurarBuscador("searchInputCalif", "calificacionesTable", "searchStatsCalif", "calificación");

}