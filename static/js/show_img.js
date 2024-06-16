// Функция для отображения увеличенного изображения при клике.
function showImage(event) {
    // Получаем ссылку на изображение, по которому был клик.
    const clickedImageSrc = event.target.src;

    // Создаем элемент увеличенного изображения.
    const enlargedImage = document.createElement('img');
    // Устанавливаем ссылку на источник увеличенного изображения.
    enlargedImage.src = clickedImageSrc;
    // Применяем класс для увеличенного изображения.
    enlargedImage.className = 'enlarged-image';

    // Создаем элемент оверлея для увеличенного изображения.
    const overlay = document.createElement('div');
    // Применяем класс для оверлея.
    overlay.className = 'image-overlay';

    // Создаем кнопку закрытия.
    const closeButton = document.createElement('div');
    // Устанавливаем HTML сущность для крестика (X).
    closeButton.innerHTML = '&#10006;';
    // Добавляем класс для стилей кнопки закрытия.
    closeButton.className = 'close-button';
    // Назначаем обработчик события клика для кнопки закрытия.
    closeButton.onclick = function() {
        // Удаляем оверлей из DOM для закрытия увеличенного изображения.
        document.body.removeChild(overlay);
    };

    // Добавляем кнопку закрытия и увеличенное изображение в оверлей.
    overlay.appendChild(closeButton);
    overlay.appendChild(enlargedImage);
    // Добавляем оверлей на страницу.
    document.body.appendChild(overlay);

    // Обработчик клика на оверлее для закрытия увеличенного изображения.
    overlay.onclick = function(event) {
        // Проверяем, если клик был по самому оверлею или по увеличенному изображению.
        if (event.target === overlay || event.target === enlargedImage) {
            // Удаляем оверлей из DOM для закрытия увеличенного изображения.
            document.body.removeChild(overlay);
        }
    };
}

// Функция для назначения обработчиков клика всем изображениям на странице.
function setupImageClickHandlers() {
    // Получаем все изображения на странице.
    const images = document.getElementsByTagName('img');
    // Назначаем обработчик события клика для каждого изображения.
    for (let i = 0; i < images.length; i++) {
        if (images[i].height > 75) { // Проверяем, что высота изображения больше 75 пикселей.
            images[i].style.cursor = 'pointer';
            images[i].onclick = showImage;
        }
    }
}

// Вызываем функцию setupImageClickHandlers после загрузки содержимого страницы.
document.addEventListener('DOMContentLoaded', function() {
    setupImageClickHandlers();
});
