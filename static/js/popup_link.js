document.addEventListener('DOMContentLoaded', function() {
    // Находим все ссылки с классом 'popup-link'
    var popupLinks = document.querySelectorAll('a.popup_link');

    // Для каждой найденной ссылки добавляем обработчик события 'click'
    popupLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault(); // Предотвращаем стандартное действие ссылки
            var url = this.href; // Получаем URL из href атрибута ссылки
            console.log('URL для открытия всплывающего окна:', url); // Логируем URL
            openPopup(url); // Вызываем функцию openPopup
        });
    });
});

// Функция для открытия всплывающего окна
function openPopup(url) {
    var width = screen.width * 0.5; // 50% от ширины экрана
    var height = screen.height * 0.5; // 50% от высоты экрана
    var left = (screen.width - width) / 2; // Центрируем по горизонтали
    var top = (screen.height - height) / 2; // Центрируем по вертикали

    var options = 'width=' + width + ',height=' + height + ',left=' + left + ',top=' + top;
    console.log('Открывается всплывающее окно с URL:', url); // Логируем URL перед открытием
    window.open(url, 'popup', options); // Открываем всплывающее окно с указанными параметрами
}
