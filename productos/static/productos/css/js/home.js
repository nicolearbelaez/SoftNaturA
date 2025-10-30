// JavaScript para el carrusel
document.addEventListener('DOMContentLoaded', function() {
    let currentImageIndex = 0;
    const images = document.querySelectorAll('.carousel-image');
    const totalImages = images.length;

    function showImage(index) {
        // Remover clase active de todas las imágenes
        images.forEach(img => img.classList.remove('active'));
        
        // Añadir clase active a la imagen actual
        images[index].classList.add('active');
    }

    function nextImage() {
        currentImageIndex = (currentImageIndex + 1) % totalImages;
        showImage(currentImageIndex);
    }

    function prevImage() {
        currentImageIndex = (currentImageIndex - 1 + totalImages) % totalImages;
        showImage(currentImageIndex);
    }

    // Event listeners para los botones
    const nextButton = document.querySelector('.carousel-button.next');
    const prevButton = document.querySelector('.carousel-button.prev');

    if (nextButton) {
        nextButton.addEventListener('click', nextImage);
    }

    if (prevButton) {
        prevButton.addEventListener('click', prevImage);
    }

    // Asegurar que la primera imagen esté visible al cargar
    showImage(0);
});