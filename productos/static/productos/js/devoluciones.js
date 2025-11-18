// ===== DATOS DE PRODUCTOS =====
const todosLosProductos = JSON.parse(document.getElementById('productosData').textContent);

// ===== CAMBIAR TABS =====
function cambiarTab(tab, event) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(tab).classList.add('active');
    event.currentTarget.classList.add('active');
}

// ===== CARGAR PRODUCTOS SEGÚN PEDIDO SELECCIONADO =====
function cargarProductos() {
    const selectPedido = document.getElementById('selectPedido');
    const selectProducto = document.getElementById('selectProducto');
    const grupoProducto = document.getElementById('grupoProducto');

    const pedidoSeleccionado = selectPedido.value;

    if (!pedidoSeleccionado) {
        grupoProducto.style.display = 'none';
        selectProducto.innerHTML = '<option value="">-- Primero selecciona un pedido --</option>';
        return;
    }

    const pedidoId = parseInt(pedidoSeleccionado);
    const productos = todosLosProductos.filter(p => p.pedido_id === pedidoId);

    selectProducto.innerHTML = '<option value="">-- Selecciona el producto --</option>';
    productos.forEach(producto => {
        const option = document.createElement('option');
        option.value = `${producto.producto_id}-${producto.unidad}`;
        option.textContent = `${producto.producto_nombre} - Unidad ${producto.unidad} - $${producto.precio}`;
        option.dataset.pedidoId = producto.pedido_id;
        selectProducto.appendChild(option);
    });

    grupoProducto.style.display = 'block';
}

// ===== SISTEMA DE FOTOS =====
let fotosCapturadas = []; // Array de File reales
const MAX_FOTOS = 3;

const btnAbrirCamara = document.getElementById('btnAbrirCamara');
const btnCerrarModal = document.getElementById('btnCerrarModal');
const btnCapturar = document.getElementById('btnCapturar');
const modalCamara = document.getElementById('modalCamara');
const videoElement = document.getElementById('videoElement');
const canvasElement = document.getElementById('canvasElement');
const previewGrid = document.getElementById('previewGrid');
const contadorFotos = document.getElementById('contadorFotos');
const inputArchivo = document.getElementById('inputArchivo');

const inputFoto1 = document.getElementById('foto1');
const inputFoto2 = document.getElementById('foto2');
const inputFoto3 = document.getElementById('foto3');

let stream = null;

// ===== FUNCIONES AUXILIARES =====
function actualizarInputs() {
    const dt1 = new DataTransfer();
    const dt2 = new DataTransfer();
    const dt3 = new DataTransfer();

    if (fotosCapturadas[0]) dt1.items.add(fotosCapturadas[0]);
    if (fotosCapturadas[1]) dt2.items.add(fotosCapturadas[1]);
    if (fotosCapturadas[2]) dt3.items.add(fotosCapturadas[2]);

    inputFoto1.files = dt1.files;
    inputFoto2.files = dt2.files;
    inputFoto3.files = dt3.files;
}

function actualizarPreview() {
    previewGrid.innerHTML = '';

    fotosCapturadas.forEach((file, index) => {
        const url = URL.createObjectURL(file);
        const div = document.createElement('div');
        div.className = 'foto-item';
        div.innerHTML = `
            <img src="${url}" alt="Foto ${index + 1}">
            <button type="button" class="btn-eliminar-foto" onclick="eliminarFoto(${index})">
                <i class="fa fa-times"></i>
            </button>
        `;
        previewGrid.appendChild(div);
    });

    for (let i = fotosCapturadas.length; i < MAX_FOTOS; i++) {
        const div = document.createElement('div');
        div.className = 'foto-item empty';
        div.innerHTML = '<i class="fa fa-image"></i>';
        previewGrid.appendChild(div);
    }

    contadorFotos.textContent = fotosCapturadas.length;

    actualizarInputs();

    btnAbrirCamara.disabled = fotosCapturadas.length >= MAX_FOTOS;
    document.querySelector('.btn-archivo').disabled = fotosCapturadas.length >= MAX_FOTOS;
}

function agregarFoto(file) {
    if (fotosCapturadas.length >= MAX_FOTOS) return;
    fotosCapturadas.push(file);
    actualizarPreview();
}

function eliminarFoto(index) {
    fotosCapturadas.splice(index, 1);
    actualizarPreview();
}

window.eliminarFoto = eliminarFoto;

// ===== CÁMARA =====
btnAbrirCamara.addEventListener('click', async () => {
    if (fotosCapturadas.length >= MAX_FOTOS) {
        alert('Ya has agregado 3 fotos (máximo permitido)');
        return;
    }

    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
        videoElement.srcObject = stream;
        modalCamara.classList.add('active');
    } catch (error) {
        alert('Error al acceder a la cámara: ' + error.message);
    }
});

btnCerrarModal.addEventListener('click', cerrarCamara);

btnCapturar.addEventListener('click', () => {
    if (fotosCapturadas.length >= MAX_FOTOS) {
        alert('Ya has agregado 3 fotos');
        cerrarCamara();
        return;
    }

    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    canvasElement.getContext('2d').drawImage(videoElement, 0, 0);

    canvasElement.toBlob(blob => {
        const file = new File([blob], `foto_${Date.now()}.jpg`, { type: 'image/jpeg' });
        agregarFoto(file);
    }, 'image/jpeg', 0.95);

    cerrarCamara();
});

function cerrarCamara() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    modalCamara.classList.remove('active');
}

// ===== SUBIR DESDE ARCHIVO =====
inputArchivo.addEventListener('change', (e) => {
    const archivos = Array.from(e.target.files);

    archivos.forEach(file => {
        if (fotosCapturadas.length >= MAX_FOTOS) {
            alert('Máximo 3 fotos permitidas');
            return;
        }
        agregarFoto(file);
    });

    inputArchivo.value = '';
});

// ===== ENVÍO DE DEVOLUCIÓN =====
const formDevolucion = document.getElementById('formDevolucion');
if (formDevolucion) {
    formDevolucion.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(formDevolucion);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(formDevolucion.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Quitar el producto devuelto
                const selectProducto = document.getElementById('selectProducto');
                const valueToRemove = `${data.producto_id}-${data.unidad}`;
                const optionProd = Array.from(selectProducto.options).find(o => o.value === valueToRemove);
                if (optionProd) optionProd.remove();

                // Quitar el pedido si no quedan productos
                const pedidoId = data.pedido_id;
                const restantes = Array.from(selectProducto.options).filter(o => {
                    return o.value !== "" && parseInt(o.dataset.pedidoId) === pedidoId;
                });
                
                if (restantes.length === 0) {
                    const selectPedido = document.getElementById('selectPedido');
                    const optionPedido = Array.from(selectPedido.options).find(o => o.value == pedidoId);
                    if (optionPedido) optionPedido.remove();
                    document.getElementById('grupoProducto').style.display = 'none';
                }

                alert(data.mensaje);
            } else {
                alert(data.mensaje);
            }
        })
        .catch(err => {
            console.error(err);
            alert('Ocurrió un error al enviar la devolución');
        });
    });
}
