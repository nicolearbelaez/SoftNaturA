document.addEventListener('DOMContentLoaded', function() {
  // --- Carrusel de imágenes ---
  let currentIndex = 0;
  const images = document.querySelectorAll('.carousel-image');
  const total = images.length;
  const prevBtn = document.querySelector('.carousel-button.prev');
  const nextBtn = document.querySelector('.carousel-button.next');

  function showImage(index) {
    images.forEach((img, i) => {
      img.classList.toggle('active', i === index);
    });
  }

  function nextImage() {
    currentIndex = (currentIndex + 1) % total;
    showImage(currentIndex);
  }

  function prevImage() {
    currentIndex = (currentIndex - 1 + total) % total;
    showImage(currentIndex);
  }

  if (nextBtn && prevBtn) {
    nextBtn.addEventListener('click', nextImage);
    prevBtn.addEventListener('click', prevImage);
  }

  showImage(currentIndex);
  setInterval(nextImage, 4000);

  // --- Carrusel de comentarios ---
  document.body.style.width = "calc(100vw - (100vw - 100%))";

  const lista = document.querySelector('.lista-comentarios');
  const prev = document.getElementById('prev-comentario');
  const next = document.getElementById('next-comentario');

  let index = 0;
  function mostrarComentario(n) {
    const total = document.querySelectorAll('.comentario-card').length;
    if (n < 0) index = total - 1;
    else if (n >= total) index = 0;
    else index = n;
    lista.style.transform = `translateX(-${index * 100}%)`;
  }

  if (next && prev) {
    next.addEventListener('click', () => mostrarComentario(index + 1));
    prev.addEventListener('click', () => mostrarComentario(index - 1));
  }

  setInterval(() => mostrarComentario(index + 1), 5000);

  // --- Avatares según nombre ---
  const comentarios = document.querySelectorAll(".comentario-card");
  const nombresFemeninos = ["sofia", "maría", "maria", "laura", "ana", "camila", "juliana", "valentina", "carolina", "paula", "isabela", "andrea"];

  comentarios.forEach(card => {
    const usuario = card.querySelector(".comentario-usuario strong").textContent.toLowerCase().trim();
    console.log("Nombre detectado:", usuario); // 👈 Aquí sí verás los nombres en la consola del navegador

    const avatar = document.createElement("img");
    avatar.classList.add("avatar");

    const esMujer = nombresFemeninos.some(nombre => usuario.includes(nombre));

    avatar.src = esMujer
      ? "/media/uploads/products/avatar_mujer.png"
      : "/media/uploads/products/avatar_hombre.png";

    card.insertBefore(avatar, card.firstChild);
  });
});