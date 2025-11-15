    document.addEventListener('DOMContentLoaded', function () {
        // Carrito
        const iconoCarrito = document.getElementById("iconoCarrito");
        const carritoDropdown = document.getElementById("carritoDropdown");

        if (iconoCarrito && carritoDropdown) {
            // Toggle manual
            iconoCarrito.onclick = function (e) {
                e.stopPropagation();
                carritoDropdown.style.display = carritoDropdown.style.display === "block" ? "none" : "block";
            };

            // Cerrar al hacer click fuera
            document.addEventListener("click", function (e) {
                if (!iconoCarrito.contains(e.target) && !carritoDropdown.contains(e.target)) {
                    carritoDropdown.style.display = "none";
                }
            });

            // 👇 Mantenerlo abierto si viene de ?carrito=1
            if (window.location.search.includes("carrito=1")) {
                carritoDropdown.style.display = "block";
            }
        }

        // MENÚ USUARIO
        const userIcon = document.getElementById('userIcon');
        const menuUsuario = document.getElementById('menuUsuario');
        if (userIcon && menuUsuario) {
            userIcon.onclick = function (e) {
                e.stopPropagation();
                menuUsuario.style.display = menuUsuario.style.display === 'block' ? 'none' : 'block';
            };
            document.addEventListener("click", function (e) {
                if (!userIcon.contains(e.target) && !menuUsuario.contains(e.target)) {
                    menuUsuario.style.display = 'none';
                }
            });
        }
    });